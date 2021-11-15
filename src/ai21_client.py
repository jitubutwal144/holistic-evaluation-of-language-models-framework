from typing import Any, Dict
import requests

from client import Client
from cache import Cache
from schemas import Request, RequestResult, Completion

# https://studio.ai21.com/docs/api/
class AI21Client(Client):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache = Cache(self.get_cache_path('ai21'))

    def make_request(self, request: Request) -> RequestResult:
        model = request.model
        if model not in ['ai21/j1-large', 'ai21/j1-jumbo']:
            raise Exception('Invalid model')
        raw_request = {
            'prompt': request.prompt,
            'temperature': request.temperature,
            'numResults': request.numSamples,  # independent
            'topKReturn': request.topK,
            'maxTokens': request.maxTokens,
            'stopSequences': request.stopSequences,
        }

        def do_it():
            return requests.post(
                f'https://api.ai21.com/studio/v1/{request.model_engine()}/complete',
                headers={'Authorization': f'Bearer {self.api_key}'},
                json=raw_request,
            ).json()
        response, cached = self.cache.get(raw_request, self.wrap_request_time(do_it))

        if 'completions' not in response:
            return RequestResult(
                success=False,
                error=response['detail'],
            )

        completions = []
        for completion in response['completions']:
            completions.append(Completion(
                text=completion['data']['text'],
            ))
        return RequestResult(
            success=True,
            cached=cached,
            requestTime=response['requestTime'],
            completions=completions,
        )
