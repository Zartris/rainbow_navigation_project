import torch
from torch import nn
import torch.nn.functional as F
from classes.models.layers import FactorizedNoisyLinear


class QNetwork(nn.Module):
    """Actor (Policy) Model."""

    def __init__(self, state_size, action_size, seed):
        """Initialize parameters and build model.
        Params
        ======
            state_size (int): Dimension of each state
            action_size (int): Dimension of each action
            seed (int): Random seed
        """
        super(QNetwork, self).__init__()
        self.seed = seed
        torch.manual_seed(self.seed)

        self.state_size = state_size
        self.action_size = action_size

        self.model = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, self.action_size)
        )

        self.model.apply(self.init_weights)

    def forward(self, state):
        """Build a network that maps state -> action values."""
        return self.model(state)

    def init_weights(self, m):
        if type(m) == nn.Linear:
            torch.nn.init.xavier_uniform_(m.weight)
            m.bias.data.fill_(0.01)


# # Dueling Deep Q-Network (DDQN)
class DDQN(nn.Module):
    def __init__(self, state_size, action_size, seed=0):
        super(DDQN, self).__init__()
        torch.manual_seed(seed)
        self.action_size = action_size
        self.state_size = state_size

        self.feature_layer = nn.Sequential(
            nn.Linear(self.state_size, 512),
            nn.ReLU()
        )

        self.value_stream = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 1)
        )

        self.advantage_stream = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, self.action_size)
        )

        self.feature_layer.apply(self.init_weights)
        self.value_stream.apply(self.init_weights)
        self.advantage_stream.apply(self.init_weights)

    def forward(self, state):
        x = self.feature_layer(state)
        value = self.value_stream(x)
        advantage = self.advantage_stream(x)
        q_values = value.expand_as(advantage) + (
                advantage - advantage.mean(dim=state.dim() - 1, keepdim=True).expand_as(advantage))
        return q_values

    @staticmethod
    def init_weights(m):
        if type(m) == nn.Linear:
            torch.nn.init.xavier_uniform_(m.weight)
            m.bias.data.fill_(0.01)


# # Noisy Dueling Deep Q-Network (Noisy-DDQN)
class NoisyDDQN(nn.Module):
    def __init__(self, state_size, action_size, seed=0, std_init=0.5):
        super(NoisyDDQN, self).__init__()
        torch.manual_seed(seed)
        self.action_size = action_size
        self.state_size = state_size

        self.feature_layer = nn.Sequential(
            nn.Linear(self.state_size, 512),
            nn.ReLU()
        )

        self.value_stream = nn.Sequential(
            FactorizedNoisyLinear(512, 512, seed, std_init=std_init, name="value_stream1"),
            nn.ReLU(),
            FactorizedNoisyLinear(512, 1, seed, std_init=std_init, name="value_stream2")
        )

        self.advantage_stream = nn.Sequential(
            FactorizedNoisyLinear(512, 512, seed, std_init=std_init, name="advantage_stream1"),
            nn.ReLU(),
            FactorizedNoisyLinear(512, self.action_size, seed, std_init=std_init, name="advantage_stream2")
        )

        self.feature_layer.apply(self.init_weights)
        self.value_stream.apply(self.init_weights)
        self.advantage_stream.apply(self.init_weights)

    def forward(self, state):
        x = self.feature_layer(state)
        value = self.value_stream(x)
        advantage = self.advantage_stream(x)
        q_values = value.expand_as(advantage) + (
                advantage - advantage.mean(dim=state.dim() - 1, keepdim=True).expand_as(advantage))
        return q_values

    def reset_noise(self):
        for module in self.modules():
            if isinstance(module, FactorizedNoisyLinear):
                module.reset_noise()

    @staticmethod
    def init_weights(m):
        if type(m) == nn.Linear:
            torch.nn.init.xavier_uniform_(m.weight)
            m.bias.data.fill_(0.01)


class DistributedNoisyDDQN(nn.Module):
    def __init__(self,
                 state_size: int,
                 action_size: int,
                 std_init: float,
                 support: torch.Tensor,
                 atom_size: int = 51,
                 seed=None):
        super(DistributedNoisyDDQN, self).__init__()
        if seed is not None:
            torch.manual_seed(seed)

        self.action_size = action_size
        self.state_size = state_size
        self.support = support
        self.atom_size = atom_size

        self.feature_layer = nn.Sequential(
            nn.Linear(self.state_size, 512),
            nn.ReLU()
        )

        self.value_stream = nn.Sequential(
            FactorizedNoisyLinear(512, 512, std_init=std_init, seed=seed, name="value_stream1"),
            nn.ReLU(),
            FactorizedNoisyLinear(512, 1 * self.atom_size, std_init=std_init, seed=seed, name="value_stream2")
        )

        self.advantage_stream = nn.Sequential(
            FactorizedNoisyLinear(512, 512, std_init=std_init, seed=seed, name="advantage_stream1"),
            nn.ReLU(),
            FactorizedNoisyLinear(512, self.action_size * self.atom_size, std_init=std_init, seed=seed,
                                  name="advantage_stream2")
        )

        self.feature_layer.apply(self.init_weights)
        self.value_stream.apply(self.init_weights)
        self.advantage_stream.apply(self.init_weights)

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        # Compute dist:
        distribution = self.get_distribution(state)
        # get q_values:
        q_values = torch.sum(distribution * self.support, dim=2)
        return q_values

    def get_distribution(self, state: torch.Tensor) -> torch.Tensor:
        # Run through model:
        x = self.feature_layer(state)
        value = self.value_stream(x).view(-1, 1, self.atom_size)
        advantage = self.advantage_stream(x).view(-1, self.action_size, self.atom_size)
        # Compute Q values for atoms
        q_atoms = value + advantage - advantage.mean(dim=1, keepdim=True)

        dist = F.softmax(q_atoms, dim=-1)  # Using softmax when working with a distribution.
        dist = dist.clamp(min=1e-3)  # To avoid nans
        return dist

    def reset_noise(self):
        for module in self.modules():
            if isinstance(module, FactorizedNoisyLinear):
                module.reset_noise()

    @staticmethod
    def init_weights(m):
        if type(m) == nn.Linear:
            torch.nn.init.xavier_uniform_(m.weight)
            m.bias.data.fill_(0.01)