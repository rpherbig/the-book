from pathlib import Path
from .dataset_generator import DatasetGenerator

preamble = """
You are helping me build a fictional scenario meant to generate a dataset for teaching sentiment analysis in emotionally charged situations.
The fictional situation in question is that of funeral home reviews on a public facing website.  It would be kind of similar to yelp for the bereaved.
Obviously no one would provide reviews of such a personal experience in a public forum, but for the sake of the exercise, let's suspend our sense of
disbelief.

The funeral home for which the reviews were generated offers the following services.

* Cremation
* Embalming
* Casket sales
* Urn sales
* Selecting & Arranging Flowers
* Producing "In Memoriam" fliers
* Sourcing speakers (e.g. ministers, rabbis, etc)
* Providing pallbearers
* Introductions to grief counselors

The ratings on the website have the following infortation:

* A star rating from 0 to 5
* The name of the service being reviewed
* A text review that is no more than 500 words long

Reviews are vetted for being from people who purchased or who attended services from the funeral home, but no other filtering mechanism is in place.  
The reviews are left on a publicly accessible forum, but are anonymized to remove information about the deceased and the berieved.
"""

all_modifiers = [
    "mourning",
    "grieving",
    "jaded",
    "in shock",
    "in denial",
    "understanding",
    "calm",
    # Below here are the users that are angry as hell
    "furious",
    "angry",
    "pissed",
]

# Used to identify if the review had an outsized negative sentiment or not
negative_review_users = [
    "furious",
    "angry",
    "pissed",
]

# used to identify if the review SHOULD have had an outsized negative sentiment or not
negative_review_specializations = [
    "because one of the funeral home's pallbearers dropped the casket.",
    "because the furnace failed and repairs took longer than anticipated.",
    "because the funeral home sent out invitations with the wrong address.",
]

common_issues = [
    (
        "The graveside ceremony was a little much ",
        [
            "but it's what they would have wanted.",
            "because there was inclement weather",
            "because it was too hot for the length of the sermon.",
            "because it was too cold for some of the more elderly attendees.",
            "because the deceased parents insisted on a religious ceremony even though the decesed was an atheist.",
            "because one of the family's pallbearers dropped the casket."
            # this is the legitimate grievance in the set.
            "because one of the funeral home's pallbearers dropped the casket.",
        ]
    ),
    (
        "Creamation happened much later than originally anticipated ",
        [
            "because the air quality index prevented the funeral home from running the furances.",
            "because a pandemic caused a spike in demand for services.",
            # this is the legitimate grievance in the set -- home should have had some spare parts
            "because the furnace failed and repairs took longer than anticipated."
        ]
    ),
    (
        "The deceased didn't look very good during their open-casket funeral ",
        [
            " because they died violently. There wasn't much that could have been done.",
            " because they shaved the deceased.  No one told them grandpa always wore a beard.",
            " because you really can't make a corpse look 'natural'.  We did a fine job, but they had unrealistic expectations.",
            " because they died in a car accident.",
            " because they insisted he be burried in his old suit, even though it didn't fit him any more."
            # no legitimate grievances in this set
        ]
    ),
    (
        "The funeral procession took far too long ",
        [
            "because the hearse broke down.",
            "because the graveyard is on the otherside of some train tracks and we got interrupted by a long train.",
            "because our police escort got called away to an emergency at the last moment.",
            "because they wouldn't listen to our advice about using a nearer graveyard or a nearer funeral home."
            "because one of the early cars stopped at a light even though they were not supposed to and lost the procession, leading everyone astray.",
            # no legitimate grievances in this set
        ]
    ),
    (
        "The funeral was poorly attended ",
        [
            "because there was an ice storm that weekend and flights were cancelled.",
            "because there was a typo in the email the family sent out, and many mourners went to the wrong address.",
            "because the deceased wasn't a very nice person when they were alive.",
            "because the funeral conflicted with the superbowl.",
            # this is the legitimate grievance in this set
            "because the funeral home sent out invitations with the wrong address."
        ]
    )
]

bases = [
    "son",
    "daughter",
    "spouse",
    "husband",
    "wife",
    "father",
    "mother",
    "friend"
]

def build_dataset(generator, cutoff=1):
    for base in bases:
        persona = generator.build_custom_personae(base, [ None ])
        queries = generator.generate_queries([ None ], persona)
        generator.get_queries(queries, cutoff)

data_location = "data/funeralhome.json" 

def add_to_dataset():
    prev_run_as_path = Path(data_location)
    requester = lambda value, base, issue, reason: f"Please find me a review from a {value} where the {base} is describing an experience like the following: {issue} {reason}"
    generator = None
    if prev_run_as_path.exists():
        generator = DatasetGenerator.load(data_location)
        generator.request_gen = requester
        print("Adding to previous run")
    else:
        generator = DatasetGenerator(common_issues, all_modifiers, preamble, tail=None, requester=requester, output_path=data_location)
    build_dataset(generator, cutoff=None)
    generator.save(data_location)
    generator.display()
