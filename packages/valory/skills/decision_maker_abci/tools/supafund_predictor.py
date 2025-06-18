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

"""This module contains the supafund predictor tool."""

import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

from openai import OpenAI
from supabase import Client, create_client


# --- Constants ---
WEIGHT_DEFINITIONS = {
    "founder": {
        "name": "Founder & Team Analysis",
        "description": "Evaluates team experience, track record, and domain expertise",
        "levels": {
            1: {"label": "Minimal Focus", "description": "Team background is secondary consideration; accept promising projects regardless of founder experience"},
            2: {"label": "Basic Consideration", "description": "Some team evaluation but willing to overlook inexperience for strong technical/market potential"},
            3: {"label": "Moderate Importance", "description": "Balanced view of team capabilities; prefer experienced founders but not dealbreaker"},
            4: {"label": "High Priority", "description": "Strong emphasis on proven track record, domain expertise, and execution capability"},
            5: {"label": "Critical Factor", "description": "Team quality is paramount; only back projects with exceptional founder pedigree and demonstrated success"}
        }
    },
    "market": {
        "name": "Market Opportunity Analysis",
        "description": "Assesses market size, growth potential, and competitive landscape",
        "levels": {
            1: {"label": "Minimal Focus", "description": "Market size less important; willing to bet on early/experimental markets with unclear demand"},
            2: {"label": "Basic Consideration", "description": "Some market validation preferred but accept niche or speculative opportunities"},
            3: {"label": "Moderate Importance", "description": "Balanced market assessment; prefer growing markets but open to emerging sectors"},
            4: {"label": "High Priority", "description": "Strong market validation required; focus on sizeable, fast-growing addressable markets"},
            5: {"label": "Critical Factor", "description": "Market opportunity must be massive and well-validated; only invest in proven, high-growth sectors"}
        }
    },
    "technical": {
        "name": "Github Analysis",
        "description": "Evaluates code quality, development activity, and technical innovation",
        "levels": {
            1: {"label": "Minimal Focus", "description": "Technical implementation secondary; focus on vision/market over current development state"},
            2: {"label": "Basic Consideration", "description": "Some technical review but accept early-stage projects with limited development activity"},
            3: {"label": "Moderate Importance", "description": "Balanced technical assessment; prefer active development but not mandatory"},
            4: {"label": "High Priority", "description": "Strong technical execution required; emphasize code quality, innovation, and development momentum"},
            5: {"label": "Critical Factor", "description": "Technical excellence paramount; only back projects with breakthrough innovation and exceptional development velocity"}
        }
    },
    "social": {
        "name": "Social/Sentiment Analysis",
        "description": "Measures community engagement, social media presence, and sentiment",
        "levels": {
            1: {"label": "Minimal Focus", "description": "Community size irrelevant; focus on fundamentals over social metrics and hype"},
            2: {"label": "Basic Consideration", "description": "Some community awareness helpful but not essential for investment decision"},
            3: {"label": "Moderate Importance", "description": "Balanced community evaluation; prefer engaged audiences but not dealbreaker"},
            4: {"label": "High Priority", "description": "Strong community essential; emphasize social proof, engagement quality, and positive sentiment"},
            5: {"label": "Critical Factor", "description": "Community dominance required; only invest in projects with massive, highly engaged, passionate communities"}
        }
    },
    "tokenomics": {
        "name": "Tokenomics Analysis",
        "description": "Analyzes token distribution, utility, and economic model",
        "levels": {
            1: {"label": "Minimal Focus", "description": "Token design secondary; accept experimental or undefined tokenomics for strong projects"},
            2: {"label": "Basic Consideration", "description": "Some token utility preferred but flexible on economic model details"},
            3: {"label": "Moderate Importance", "description": "Balanced tokenomics review; prefer clear utility but open to innovative approaches"},
            4: {"label": "High Priority", "description": "Strong tokenomics required; emphasize sustainable economics, clear utility, and fair distribution"},
            5: {"label": "Critical Factor", "description": "Tokenomics excellence mandatory; only invest in projects with revolutionary economic models and perfect token design"}
        }
    }
}
DEFAULT_USER_WEIGHTS = {
    "founder": 3,
    "market": 3,
    "technical": 3,
    "social": 3,
    "tokenomics": 3,
}

# --- API Clients ---

class LLMClient:
    """A client to interact with a Large Language Model."""
    def __init__(self, api_key: str):
        self._api_key = api_key
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=self._api_key)

    def make_prediction_request(self, prompt: str) -> Dict[str, Any]:
        """Makes a prediction request to the LLM."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error calling OpenAI: {e}")
            return {"prediction": "ERROR", "confidence": 0.0, "reasoning": str(e)}


class SupafundClient:
    """A client for interacting with the Supafund Supabase database."""
    def __init__(self, url: str, key: str):
        if not url or not key:
            raise ValueError("Supabase URL or key is not set.")
        self.client: Client = create_client(url, key)

    def get_application(self, application_id: str) -> Dict[str, Any]:
        """Fetches a single application by its ID."""
        try:
            result = self.client.table("applications").select("*").eq("id", application_id).single().execute()
            return result.data
        except Exception as e:
            logging.error(f"Error fetching application {application_id} from Supabase: {e}")
            raise

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Fetches project and its related data by project ID."""
        try:
            project_result = self.client.table("projects").select("*").eq("id", project_id).single().execute()
            return project_result.data
        except Exception as e:
            logging.error(f"Error fetching project {project_id} from Supabase: {e}")
            raise

    def get_program(self, program_id: str) -> Dict[str, Any]:
        """Fetches program details by program ID."""
        try:
            program_result = self.client.table("programs").select("*, rounds(*)").eq("id", program_id).single().execute()
            return program_result.data
        except Exception as e:
            logging.error(f"Error fetching program {program_id} from Supabase: {e}")
            raise


class FeatureAssembler:
    """Assembles features for the prediction model."""

    def assemble_features(
        self,
        project_data: Dict[str, Any],
        program_data: Dict[str, Any],
        user_weights: Dict[str, int],
    ) -> Dict[str, Any]:
        """Assembles a dictionary of features from various data sources."""
        features = {
            "project_name": project_data.get("name"),
            "project_description": project_data.get("description"),
            "program_fit_score": self._calculate_program_fit(project_data, program_data),
            "application_quality_score": self._score_application_quality(project_data),
            "user_priorities": self._format_user_priorities(user_weights),
        }
        return features

    def _calculate_program_fit(self, project_data: Dict, program_data: Dict) -> float:
        # Dummy implementation, replace with actual logic
        return 0.85

    def _score_application_quality(self, project_data: Dict) -> float:
        # Dummy implementation, replace with actual logic
        return 0.95

    def _format_user_priorities(self, user_weights: Dict[str, int]) -> str:
        """Formats user priorities into a descriptive string."""
        priority_statements = []
        for weight_key, level in user_weights.items():
            if weight_key in WEIGHT_DEFINITIONS:
                definition = WEIGHT_DEFINITIONS[weight_key]
                level_info = definition["levels"].get(level)
                if level_info:
                    statement = f"- **{definition['name']}**: You've set this to **Level {level} ({level_info['label']})**, meaning: *{level_info['description']}*"
                    priority_statements.append(statement)
        return "\n".join(priority_statements)


class PredictionEngine:
    """Handles the prediction logic by interacting with the LLM."""

    def __init__(self, llm_client: LLMClient):
        self._llm_client = llm_client

    def predict(self, application_id: str, market_question: str, features: Dict[str, Any]) -> Dict[str, Any]:
        """Makes a prediction based on the assembled features."""
        prompt = self._build_prediction_prompt(application_id, market_question, features)
        prediction = self._llm_client.make_prediction_request(prompt)
        return prediction

    def _build_prediction_prompt(self, application_id: str, market_question: str, features: Dict[str, Any]) -> str:
        """Builds the comprehensive prompt for the LLM."""
        prompt = f"""
Please act as an expert venture capital analyst. Your task is to predict the likelihood of success for a startup based on the provided data.

**Market Question:** "{market_question}"
**Application ID:** {application_id}

**Project Information:**
- **Name:** {features.get('project_name')}
- **Description:** {features.get('project_description')}

**Analysis Scores:**
- **Program Fit Score:** {features.get('program_fit_score'):.2f}/1.0
- **Application Quality Score:** {features.get('application_quality_score'):.2f}/1.0

**Your Investment Priorities:**
{features.get('user_priorities')}

**Request:**
Based on all the information above, please provide a JSON-formatted response with your prediction. The JSON object should include:
1.  `prediction`: Your prediction, either "Yes" or "No".
2.  `confidence`: Your confidence in the prediction, as a float between 0.0 and 1.0.
3.  `reasoning`: A brief explanation for your decision, highlighting the key factors based on the provided data and priorities.

Example JSON response:
{{
  "prediction": "Yes",
  "confidence": 0.85,
  "reasoning": "The project shows strong alignment with the program goals and a high-quality application. The team's background, although not a top priority, seems solid enough to execute the vision."
}}
"""
        return prompt


class SupafundPredictor:
    """Orchestrates the prediction process."""

    def __init__(self):
        self.supafund_client = SupafundClient(
            url=os.getenv("NEXT_PUBLIC_SUPABASE_URL"),
            key=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        self.llm_client = LLMClient(api_key=os.getenv("OPENAI_API_KEY"))
        self.feature_assembler = FeatureAssembler()
        self.prediction_engine = PredictionEngine(self.llm_client)

    def run(self, market_question: str) -> Dict[str, Any]:
        """
        Runs the full prediction pipeline.

        :param market_question: The question from the prediction market.
        :return: A dictionary with the prediction result.
        """
        match = re.search(r"application_id '([^']*)'", market_question)
        if not match:
            raise ValueError("Could not parse application_id from the market question.")
        application_id = match.group(1)

        try:
            # 1. Get data from Supabase
            application_data = self.supafund_client.get_application(application_id)
            project_data = self.supafund_client.get_project(application_data['project_id'])
            program_data = self.supafund_client.get_program(application_data['program_id'])

            # 2. Assemble features
            features = self.feature_assembler.assemble_features(
                project_data=project_data,
                program_data=program_data,
                user_weights=DEFAULT_USER_WEIGHTS,
            )

            # 3. Make prediction
            prediction = self.prediction_engine.predict(
                application_id=application_id,
                market_question=market_question,
                features=features
            )
            return prediction

        except Exception as e:
            logging.error(f"An error occurred during the prediction pipeline for application {application_id}: {e}")
            return {"prediction": "ERROR", "confidence": 0.0, "reasoning": str(e)}

def run_prediction(market_question: str) -> Dict[str, Any]:
    """Standalone function to run the Supafund predictor."""
    return SupafundPredictor().run(market_question) 