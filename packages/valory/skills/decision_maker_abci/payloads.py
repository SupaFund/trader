# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2023-2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the transaction payloads of the decision_maker_abci app."""

from dataclasses import dataclass
from typing import Optional

from packages.valory.skills.abstract_round_abci.base import BaseTxPayload, MultisigTxPayload


@dataclass(frozen=True)
class BlacklistingPayload(BaseTxPayload):
    """Represents a transaction payload for blacklisting."""
    policy: str
    utilized_tools: str


@dataclass(frozen=True)
class BetPlacementPayload(MultisigTxPayload):
    """Represents a transaction payload for placing a bet."""
    policy: str
    utilized_tools: str
    vote: Optional[int]
    confidence: Optional[float]
    bet_amount: Optional[int]


@dataclass(frozen=True)
class HandleFailedTxPayload(BaseTxPayload):
    """Represents a transaction payload for the HandleFailedTxRound."""
    event: str


@dataclass(frozen=True)
class RandomnessPayload(BaseTxPayload):
    """Represents a transaction payload for the RandomnessRound."""
    round_id: int
    randomness: str


@dataclass(frozen=True)
class CheckBenchmarkingPayload(BaseTxPayload):
    """Represents a transaction payload for the CheckBenchmarkingRound."""
    kick_out: bool


@dataclass(frozen=True)
class ClaimSubscriptionPayload(BaseTxPayload):
    """Represents a transaction payload for the ClaimSubscriptionRound."""
    claim_successful: bool


@dataclass(frozen=True)
class PredictionPayload(BaseTxPayload):
    """Represents a transaction payload for the PredictionRound."""
    prediction_event: str


@dataclass(frozen=True)
class SamplingPayload(BaseTxPayload):
    """Represents a transaction payload for the sampling of a bet."""
    index: Optional[int]


@dataclass(frozen=True)
class RedeemPayload(MultisigTxPayload):
    """Represents a transaction payload for preparing an on-chain transaction for redeeming."""


@dataclass(frozen=True)
class SubscriptionPayload(MultisigTxPayload):
    """Represents a transaction payload for subscribing."""
