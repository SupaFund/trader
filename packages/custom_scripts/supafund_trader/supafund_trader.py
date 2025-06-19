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

"""This module contains the supafund_trader strategy."""

from typing import Dict, Any, List, Union

REQUIRED_FIELDS = frozenset(
    {
        "bankroll",
        "win_probability",
        "confidence",
        "selected_type_tokens_in_pool",
        "other_tokens_in_pool",
        "bet_fee",
        "floor_balance",
    }
)
OPTIONAL_FIELDS = frozenset({"max_bet"})
ALL_FIELDS = REQUIRED_FIELDS.union(OPTIONAL_FIELDS)
DEFAULT_MAX_BET = 8e17

def check_missing_fields(kwargs: Dict[str, Any]) -> List[str]:
    """Check for missing fields and return them, if any."""
    missing = []
    for field in REQUIRED_FIELDS:
        if kwargs.get(field, None) is None:
            missing.append(field)
    return missing

def remove_irrelevant_fields(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Remove the irrelevant fields from the given kwargs."""
    return {key: value for key, value in kwargs.items() if key in ALL_FIELDS}

def get_supafund_prediction(**kwargs) -> Dict[str, Union[float, List[str]]]:
    """
    This is where your supafund-trader's prediction logic will go.
    It should return a dictionary with "p_yes", "p_no", and "confidence".
    """
    print(f"Supafund trader received kwargs: {kwargs}")
    # Placeholder prediction logic
    p_yes = 0.6
    p_no = 0.4
    confidence = 0.8
    return {
        "p_yes": p_yes,
        "p_no": p_no,
        "confidence": confidence,
        "info": ["Supafund prediction completed."],
        "error": []
    }

def run(*_args, **kwargs) -> Dict[str, Union[int, float, List[str]]]:
    """
    Main entry point for the supafund_trader strategy.
    This function will be called by the Olas agent.
    """
    info = []
    error = []

    missing = check_missing_fields(kwargs)
    if len(missing) > 0:
        error.append(f"Required kwargs {missing} were not provided for supafund_trader.")
        return {"bet_amount": 0, "p_yes": 0.0, "p_no": 0.0, "confidence": 0.0, "info": info, "error": error}

    relevant_kwargs = kwargs

    prediction_results = get_supafund_prediction(**relevant_kwargs)
    info.extend(prediction_results.get("info", []))
    error.extend(prediction_results.get("error", []))

    if prediction_results.get("error"):
        return {"bet_amount": 0, "p_yes": 0.0, "p_no": 0.0, "confidence": 0.0, "info": info, "error": error}

    p_yes = prediction_results["p_yes"]
    p_no = prediction_results["p_no"]
    confidence = prediction_results["confidence"]

    bet_amount = 0
    if confidence > 0.75:
        if "bankroll" in relevant_kwargs and "floor_balance" in relevant_kwargs:
            bankroll_adj = relevant_kwargs["bankroll"] - relevant_kwargs["floor_balance"]
            if bankroll_adj > 0:
                bet_amount = int(bankroll_adj * 0.01) # Bet 1%
                info.append(f"Calculated placeholder bet_amount: {bet_amount}")
        else:
            info.append("Bankroll not available for placeholder bet sizing.")
    else:
        info.append("Confidence below threshold, placeholder bet_amount is 0.")

    return {
        "bet_amount": bet_amount,
        "p_yes": p_yes,
        "p_no": p_no,
        "confidence": confidence,
        "info": info,
        "error": error,
    }

if __name__ == "__main__":
    test_kwargs = {
        "bankroll": 1000 * 10**18,
        "win_probability": 0.0,
        "confidence": 0.0,
        "selected_type_tokens_in_pool": 500 * 10**18,
        "other_tokens_in_pool": 500 * 10**18,
        "bet_fee": int(0.02 * 10**18),
        "floor_balance": 100 * 10**18,
        "some_other_data_supafund_needs": "example_value"
    }
    result = run(**test_kwargs)
    print(f"Strategy result: {result}")
