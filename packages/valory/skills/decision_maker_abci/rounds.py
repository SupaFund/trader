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

"""This module contains the data classes for the decision maker."""

from enum import Enum
from typing import Dict, Set, Type

from packages.valory.skills.abstract_round_abci.base import AbciApp
from packages.valory.skills.decision_maker_abci.states.bet_placement import (
    BetPlacementRound,
)
from packages.valory.skills.decision_maker_abci.states.blacklisting import (
    BlacklistingRound,
)
from packages.valory.skills.decision_maker_abci.states.check_benchmarking import (
    CheckBenchmarkingModeRound,
)
from packages.valory.skills.decision_maker_abci.states.claim_subscription import ClaimRound
from packages.valory.skills.decision_maker_abci.states.final_states import (
    BenchmarkingDoneRound,
    BenchmarkingModeDisabledRound,
    FinishedDecisionMakerRound,
    FinishedSubscriptionRound,
    FinishedWithoutDecisionRound,
    FinishedWithoutRedeemingRound,
    ImpossibleRound,
    RefillRequiredRound,
)
from packages.valory.skills.decision_maker_abci.states.handle_failed_tx import (
    HandleFailedTxRound,
)
from packages.valory.skills.decision_maker_abci.states.order_subscription import (
    SubscriptionRound,
)
from packages.valory.skills.decision_maker_abci.states.prediction import PredictionRound
from packages.valory.skills.decision_maker_abci.states.randomness import (
    BenchmarkingRandomnessRound,
    RandomnessRound,
)
from packages.valory.skills.decision_maker_abci.states.redeem import RedeemRound
from packages.valory.skills.decision_maker_abci.states.sampling import SamplingRound


class Event(Enum):
    """Event enumeration for the decision maker."""

    DONE = "done"
    NONE = "none"
    NO_MAJORITY = "no_majority"
    ROUND_TIMEOUT = "round_timeout"
    UNPROFITABLE = "unprofitable"
    FETCH_ERROR = "fetch_error"
    TIE = "tie"
    MECH_RESPONSE_ERROR = "mech_response_error"
    INSUFFICIENT_BALANCE = "insufficient_balance"
    SLOTS_UNSUPPORTED_ERROR = "slots_unsupported_error"
    NO_REDEEMING = "no_redeeming"
    REDEEM_ROUND_TIMEOUT = "redeem_round_timeout"
    MOCK_TX = "mock_tx"
    MOCK_MECH_REQUEST = "mock_mech_request"
    BLACKLIST = "blacklist"
    NO_OP = "no_op"
    CALC_BUY_AMOUNT_FAILED = "calc_buy_amount_failed"
    BENCHMARKING_ENABLED = "benchmarking_enabled"
    BENCHMARKING_DISABLED = "benchmarking_disabled"
    BENCHMARKING_FINISHED = "benchmarking_finished"
    NEW_SIMULATED_RESAMPLE = "new_simulated_resample"
    NO_SUBSCRIPTION = "no_subscription"
    SUBSCRIPTION_ERROR = "subscription_error"


class DecisionMakerAbciApp(AbciApp[Event]):
    """DecisionMakerAbciApp

    Initial round: CheckBenchmarkingModeRound

    Initial states: {CheckBenchmarkingModeRound, ClaimRound, HandleFailedTxRound, RandomnessRound, RedeemRound}

    Transition states:
        ClaimRound
        HandleFailedTxRound
        RandomnessRound
        BenchmarkingRandomnessRound
        SubscriptionRound
        SamplingRound
        PredictionRound
        BetPlacementRound
        RedeemRound
        BlacklistingRound
        CheckBenchmarkingModeRound

    Final states: {BenchmarkingDoneRound, BenchmarkingModeDisabledRound, FinishedDecisionMakerRound, FinishedSubscriptionRound, FinishedWithoutDecisionRound, FinishedWithoutRedeemingRound, ImpossibleRound, RefillRequiredRound}

    Timeouts:
        round timeout: 30.0
        redeem round timeout: 60.0
    """

    initial_round_cls: Type = CheckBenchmarkingModeRound
    transition_function: Dict = {
        ClaimRound: {
            Event.DONE: SamplingRound,
            Event.NO_MAJORITY: ClaimRound,
            Event.ROUND_TIMEOUT: ClaimRound,
            Event.SUBSCRIPTION_ERROR: ClaimRound,
        },
        HandleFailedTxRound: {
            Event.NO_OP: RedeemRound,
            Event.BLACKLIST: BlacklistingRound,
            Event.NO_MAJORITY: HandleFailedTxRound,
        },
        RandomnessRound: {
            Event.DONE: SamplingRound,
            Event.ROUND_TIMEOUT: RandomnessRound,
            Event.NO_MAJORITY: RandomnessRound,
            Event.NONE: ImpossibleRound,
        },
        BenchmarkingRandomnessRound: {
            Event.DONE: SamplingRound,
            Event.ROUND_TIMEOUT: BenchmarkingRandomnessRound,
            Event.NO_MAJORITY: BenchmarkingRandomnessRound,
            Event.NONE: ImpossibleRound,
        },
        SubscriptionRound: {
            Event.DONE: FinishedSubscriptionRound,
            Event.NO_SUBSCRIPTION: SamplingRound,
            Event.SUBSCRIPTION_ERROR: SubscriptionRound,
            Event.NO_MAJORITY: SubscriptionRound,
            Event.ROUND_TIMEOUT: SubscriptionRound,
            Event.NONE: SubscriptionRound,
            Event.MOCK_TX: SamplingRound,
        },
        SamplingRound: {
            Event.DONE: SubscriptionRound,
            Event.BENCHMARKING_ENABLED: PredictionRound,
            Event.NONE: FinishedWithoutDecisionRound,
            Event.FETCH_ERROR: ImpossibleRound,
            Event.NO_MAJORITY: SamplingRound,
            Event.ROUND_TIMEOUT: SamplingRound,
            Event.BENCHMARKING_FINISHED: BenchmarkingDoneRound,
            Event.NEW_SIMULATED_RESAMPLE: SamplingRound,
        },
        PredictionRound: {
            Event.DONE: BetPlacementRound,
            Event.UNPROFITABLE: BlacklistingRound,
            Event.ROUND_TIMEOUT: PredictionRound,
            Event.NO_MAJORITY: PredictionRound,
        },
        BetPlacementRound: {
            Event.DONE: FinishedDecisionMakerRound,
            Event.INSUFFICIENT_BALANCE: RefillRequiredRound,
            Event.NO_MAJORITY: BetPlacementRound,
            Event.ROUND_TIMEOUT: BetPlacementRound,
            Event.NONE: ImpossibleRound,
            Event.MOCK_TX: RedeemRound,
            Event.CALC_BUY_AMOUNT_FAILED: HandleFailedTxRound,
        },
        RedeemRound: {
            Event.DONE: FinishedDecisionMakerRound,
            Event.NO_REDEEMING: FinishedWithoutRedeemingRound,
            Event.REDEEM_ROUND_TIMEOUT: FinishedWithoutRedeemingRound,
            Event.NO_MAJORITY: RedeemRound,
            Event.NONE: ImpossibleRound,
            Event.MOCK_TX: SamplingRound,
        },
        BlacklistingRound: {
            Event.DONE: FinishedWithoutDecisionRound,
            Event.NO_MAJORITY: BlacklistingRound,
            Event.ROUND_TIMEOUT: BlacklistingRound,
            Event.NONE: ImpossibleRound,
            Event.FETCH_ERROR: ImpossibleRound,
            Event.MOCK_TX: FinishedWithoutDecisionRound,
        },
        CheckBenchmarkingModeRound: {
            Event.BENCHMARKING_ENABLED: BenchmarkingRandomnessRound,
            Event.BENCHMARKING_DISABLED: BenchmarkingModeDisabledRound,
            Event.SUBSCRIPTION_ERROR: ImpossibleRound,
            Event.NO_MAJORITY: CheckBenchmarkingModeRound,
            Event.ROUND_TIMEOUT: CheckBenchmarkingModeRound,
            Event.NONE: ImpossibleRound,
            Event.DONE: ImpossibleRound,
        },
    }
    final_states: Set[Type] = {
        FinishedDecisionMakerRound,
        FinishedWithoutDecisionRound,
        ImpossibleRound,
        BenchmarkingDoneRound,
        BenchmarkingModeDisabledRound,
        FinishedWithoutRedeemingRound,
        RefillRequiredRound,
        FinishedSubscriptionRound,
    }
    db_pre_conditions: Dict[Type, Set[str]] = {
        BenchmarkingRandomnessRound: set(),
        BetPlacementRound: {
            "most_voted_randomness",
            "participant_to_sampling",
        },
        BlacklistingRound: {
            "most_voted_randomness",
            "participant_to_sampling",
        },
        CheckBenchmarkingModeRound: set(),
        ClaimRound: {"most_voted_randomness", "participant_to_sampling"},
        HandleFailedTxRound: set(),
        RandomnessRound: set(),
        RedeemRound: {"most_voted_randomness", "participant_to_sampling"},
        SamplingRound: {"most_voted_randomness"},
        SubscriptionRound: set(),
    }
    db_post_conditions: Dict[Type, Set[str]] = {
        BenchmarkingDoneRound: set(),
        BenchmarkingModeDisabledRound: set(),
        BenchmarkingRandomnessRound: {"most_voted_randomness"},
        BetPlacementRound: {"tx_hashes_history"},
        BlacklistingRound: {"participant_to_blacklist"},
        CheckBenchmarkingModeRound: set(),
        ClaimRound: {"participant_to_subscription"},
        FinishedDecisionMakerRound: set(),
        FinishedSubscriptionRound: set(),
        FinishedWithoutDecisionRound: set(),
        FinishedWithoutRedeemingRound: set(),
        HandleFailedTxRound: set(),
        ImpossibleRound: set(),
        RandomnessRound: {"most_voted_randomness"},
        RedeemRound: {"participant_to_redeem"},
        RefillRequiredRound: set(),
        SamplingRound: {"participant_to_sampling"},
        SubscriptionRound: {"participant_to_subscription"},
    }

    event_to_timeout: Dict = {
        Event.ROUND_TIMEOUT: 30.0,
        Event.REDEEM_ROUND_TIMEOUT: 60.0,
    }
    cross_period_persisted_keys: Set[str] = {
        "tx_hashes_history",
        "participant_to_blacklist",
    }
