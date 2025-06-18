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

"""This module contains the behaviour of the skill which is responsible for making predictions."""

from typing import Generator

from packages.valory.skills.decision_maker_abci.behaviours.base import (
    DecisionMakerBaseBehaviour,
)
from packages.valory.skills.decision_maker_abci.payloads import PredictionPayload
from packages.valory.skills.decision_maker_abci.states.base import Event
from packages.valory.skills.decision_maker_abci.states.prediction import (
    PredictionRound,
)
from packages.valory.skills.decision_maker_abci.tools.supafund_predictor import (
    run_prediction,
)


class PredictionBehaviour(DecisionMakerBaseBehaviour):
    """A behaviour in which the agents make a prediction."""

    matching_round = PredictionRound

    def async_act(self) -> Generator:
        """Do the action."""
        with self.context.benchmark_tool.measure(self.behaviour_id).local():
            # Get the current market question
            question = self.synchronized_data.sampled_bet.question
            self.context.logger.info(f"Making prediction for market: {question}")

            # Run the prediction
            prediction_result = run_prediction(question)
            self.context.logger.info(f"Prediction result: {prediction_result}")

            # For now, let's consider any "Yes" prediction with confidence > 0.5 as profitable
            # This logic can be refined later.
            is_profitable = (
                prediction_result.get("prediction") == "Yes"
                and prediction_result.get("confidence", 0.0) > 0.5
            )

            if is_profitable:
                event = Event.DONE.value
            else:
                event = Event.UNPROFITABLE.value

            self.context.logger.info(f"Prediction result leads to event: {event}")
            payload = PredictionPayload(
                self.context.agent_address,
                prediction_event=event,
            )

        yield from self.finish_behaviour(payload) 