from itertools import chain
import json
from .llm_iface import Client

class DatasetGenerator:

    common_issues = None
    generic_modifiers = None
    preamble = None
    results = {}
    client = None
    tail = None
    request_gen = None
    output_path = None

    def __init__(self, common_issues=[None], generic_modifiers=[None], preamble="", tail="", requester=None, n=1, output_path=None):
        self.client = Client(n=n)
        self.common_issues = common_issues
        self.preamble = preamble
        self.generic_modifiers = generic_modifiers
        self.tail = tail
        self.request_gen = requester
        self.output_path = output_path

    def build_custom_personae(self, base, specific_modifiers):
        for modifier in self.generic_modifiers:
            for specific_modifier in specific_modifiers:
                result = {
                    "modifiers": [],
                    "base": base,
                    "value": base,
                }
                if modifier is not None:
                    result["modifiers"].append(modifier)
                    result["value"] = f"{modifier} {result["value"]}"
                if specific_modifier is not None:
                    result["modifiers"].append(specific_modifier)
                    result["value"] = f"{specific_modifier} {result["value"]}"
                yield result


    def build_query_dicts(self, all_issues, entity):
        for issue, reasons in all_issues:
                if reasons is None:
                    continue
                for reason in reasons:
                    if reason is None:
                        continue
                    yield {
                        "entity": entity,
                        "issue": issue,
                        "reason": reason,
                        # This is too tied to the IT situation.  Part of the reason why it's been so hard to get things done.
                        # TODO: Pull request into the setup step.
                        "request" : self.request_gen(entity["value"], entity["base"], issue, reason),
                        "tail" : self.tail
                    }


    def generate_queries(self, specific_issues, entities):
        all_issues = self.common_issues + specific_issues
        issues = []
        for issue in all_issues:
            if issue is None:
                continue
            else:
                issues.append(issue)
        if len(issues) == 0:
            return []
        return chain.from_iterable(map(lambda x: self.build_query_dicts(issues, x), entities))



    def get_queries(self, queries, max_query=1):
        last_entity = None
        for count, query_dict in enumerate(queries):
            situation = f"{query_dict["request"]}"
            base_entity = query_dict["entity"]["base"]
            full_entity = query_dict["entity"]["value"]
            if base_entity != last_entity:
                print(f"Querying for {base_entity}")
                last_entity = base_entity
            if query_dict["tail"] is not None:
                situation = f"{situation}\n{query_dict["tail"]}"
            chat_completion = self.client.query(self.preamble, situation)
            query_responses = []
            for choice in chat_completion.choices:
                query_responses.append(choice.message.content)
            if base_entity not in self.results:
                self.results[base_entity] = {}
            if full_entity not in self.results[base_entity]:
                self.results[base_entity][full_entity] = {}
            if query_dict["issue"] not in self.results[base_entity][full_entity]:
                self.results[base_entity][full_entity][query_dict["issue"]] = {}
            if query_dict["reason"] not in self.results[base_entity][full_entity][query_dict["issue"]]:
                self.results[base_entity][full_entity][query_dict["issue"]][query_dict["reason"]] = query_responses
            else:
                self.results[base_entity][full_entity][query_dict["issue"]][query_dict["reason"]] += query_responses
            if max_query is not None and max_query > count:
                return
            if count % 10 == 0:
                print("saving progress...")
                self.save()


    @staticmethod
    def _display_dict(d, indent_level=0):
        for key, value in d.items():
            prefix = "\t" * indent_level
            if type(value) is dict:
                print(f"{prefix}{key}:")
                DatasetGenerator._display_dict(value, indent_level + 1)
            elif type(value) is list:
                print(f"{prefix}{key}:")
                for item in value:
                    print(item)
                    print("===================================================")
            else:
                print(f"{prefix}{key}: {value}")

    def display(self):
        self._display_dict(self.results)

    def as_dict(self):
        return {
            "results" : self.results,
            "common_issues" : self.common_issues,
            "generic_modifiers" : self.generic_modifiers,
            "preamble" : self.preamble,
            "tail" : self.tail,
            "output_path" : self.output_path
        }
    
    @staticmethod
    def from_dict(d):
        ret = DatasetGenerator()
        ret.results = d["results"]
        ret.common_issues = d["common_issues"]
        ret.generic_modifiers = d["generic_modifiers"]
        ret.preamble = d["preamble"]
        ret.tail = d["tail"]
        ret.output_path = d["output_path"]
        return ret
    
    @staticmethod
    def load(path):
        with open(path, "r") as f:
            dict = json.load(f)
            return DatasetGenerator.from_dict(dict)
        
    def save(self,path=None):
        target = path if path is not None else self.output_path
        with open(target, "w") as f:
            dict = self.as_dict()
            json.dump(dict, f, indent=1)