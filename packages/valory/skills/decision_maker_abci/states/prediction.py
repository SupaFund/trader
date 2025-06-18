# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
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

"""This module contains the prediction state of the decision-making abci app."""

from packages.valory.skills.abstract_round_abci.base import (
    CollectSameUntilThresholdRound,
    get_name,
)
from packages.valory.skills.decision_maker_abci.payloads import PredictionPayload
from packages.valory.skills.decision_maker_abci.states.base import (
    Event,
    SynchronizedData,
)


class PredictionRound(CollectSameUntilThresholdRound):
    """A round for performing predictions."""

    payload_class = PredictionPayload
    synchronized_data_class = SynchronizedData
    done_event = Event.DONE
    none_event = Event.NONE
    no_majority_event = Event.NO_MAJORITY
    collection_key = get_name(SynchronizedData.participant_to_prediction)

    def end_block(self) -> None:
        """End block."""
        super().end_block()
        if self.threshold_reached:
            # We need to agree on a single prediction event, so we select the most voted one.
            # If there is a tie, we select the one with the lexicographically smallest value.
            # This is to make sure that all agents select the same event.
            prediction_event = max(self.most_voted_payload_with_threshold, key=self.most_voted_payload_with_threshold.get)
            self.synchronized_data.update(
                participant_to_prediction=self.collection,
                most_voted_prediction=prediction_event,
            ) 