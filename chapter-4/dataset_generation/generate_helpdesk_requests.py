from pathlib import Path
from .dataset_generator import DatasetGenerator

preamble ="""
You are a helpful database admin for a database that contains emails for an IT help desk.
The help desk supports an internal sales tool that is accessed via a web portal.
Internally, the sales tool is called the sales portal.
Customers refer to the sales tool as CoolCo's Website.
This sales tool is vital to the sales team as well as the company.
The sales tool is used by sales representatives to manage their sales pipeline, track their sales activities, and communicate with their customers.
Sales in this company are seasonal, with the busiest time of year being February and November.

The sales tool is comprised of several components:
* A customer database
* A product database
* Login and authentication system
* A sales pipeline for each sales representative
* A messaging system
* An export system

The sales tool is hosted in AWS on multiple EC2 instances. The databases are hosted in RDS. The sales tool is accessed via a web portal that is hosted on an S3 bucket.
The sales tool is written in Python and uses the Flask framework.

Unfortunately, the issue tracking system doesn't allow users to log what part of the system the user believes is causing issues.
When asked, please provide emails that are relevant to a particular part of the system and requested user persona.
"""
all_modifiers = [
    "young",
    "old",
    "new",
    "anxious",
    "angry",
    "technologically savvy",
    "technologically challenged",
    None,
]

customer_modifiers = [
    "high-spending",
    "returning",
    None,
]

salesperson_modifiers = [
    "high-performing",
    "struggling",
    "low-performing",
    None,
]

mechanic_modifiers = [
    "dealership operated",
    "independent",
    "from a large shop",
    "sole proprietor",
    None
]

manufacturer_modifiers = [
    "assembly line working",
    "shift captain",
    "facility manager",
    "plant mechanic",
    None
]

specific_modifiers = {
    "customer" : customer_modifiers,
    "salesperson" : salesperson_modifiers,
    "mechanic" : mechanic_modifiers,
    "manufacturer" : manufacturer_modifiers,
}

attacker_models = [
    "skilled social engineer",
    "script kiddie",
    "sophisticated hacker",
    "insider threat",
]

# Issue x Reason List
common_issues = [
# Login Issues
    (
        "Their login credentials are not working ",
        [
            "because they are not typing them correctly.",
            "because their account was flagged for suspicious activity.",
            "because their password was found in a list of compromised passwords."
        ]
    ), (
        "They can't log in ",
     [
         "because they forgot their password.",
         "because they forgot their username.",
         "because they are using the wrong URL.",
         "because their has been suspicious account activity causing the account to be locked.",
         "because they are not yet in the system."
      ]
    ), (
        "They can't access the site ",
        [
            "because they have no network connection.",
            "because the site is down for a scheduled migration.",
            "because several EC2 instances are down.",
            "because the S3 bucket is down.",
        ]
    ),
    (
        "They're directed to a different page than they expected ",
        [
            "because they've been entered into the system as the wrong type of entity.",
            "because they are multiple types of entities in the system, and have logged into the wrong account."
        ]
    ),
    # Site Responsiveness issues
    (
        "They are having trouble navigating the site and accomplishing tasks ",
        [
            "because they are novices in the system.",
            "because the site is unresponsive due to a DDOS.",
            "because the site is unresponsive due to a problem with their PC.",
            "because they were inebriated when using the site."
        ]
    )
]

# This level is a possible target for clustering, 
# but if we have email addresses, that is better done via regexp.
customer_issues = [ 
    (
        # This level is another good target for clustering.
        # It identifies the user story, and that's going to narrow down the culprit.
        "They can't access the product catalog ",
        [
            # You could do clustering here, but things like "database" are going to potentially mean
            # radically different things between issue entries.  A customer may interact with multiple
            # databases (e.g. one for products, one for maintenance), and we might not get cleanly separated
            # root cause clusters as a result.
            "because the database has failed preventing the catalog from loading.",
            "because a routing table is preventing the production server from accessing the database.",
            "because the S3 bucket is down.",
            "because they can't access the site at all.  They haven't even successfully logged in, this is just how they describe the problem.",
        ]
    ),
    (
        "They select one product from the catalog, but are directed to a different product's detail page ",
        [
            "because the product database had a data entry issue.",
            "because the web portal mangled the product id string.",
            "because they had multiple tabs open and got confused. The issue didn't really happen.",
        ]
    ),
    (
        "They can't add a product to their cart ",
        [
            "because the product database had a data entry issue.",
            "because the web portal mangled the product id string.",
            "because they had multiple tabs open and got confused. The issue didn't really happen.",
            "because they are not logged in.",
            "because the production database failed preventing the cart from loading.",
        ]
    ),
    (
        "They can't check out with their cart ",
        [
            "because the production database failed preventing us from recording the transaction.",
            "because their card was declined.",
            "because they misentered their card information.",
            "because the card information and delivery address are radically different."
            "because the card processor is down.",
            "because they are from an ITAR controlled country.",
            "because the product they are buying has since been discontinued."
        ]
    )
]

salesperson_issues = [
    (
        "They can't find a customer in their pipeline ",
        [
            "because they misspelled the name.",
            "because the customer is assigned to another salesperson.",
            "because the customer hasn't purchased from the company in over 5 years and their record was deleted.",
            "because the customer has married and changed their last name.",
            "because there was a bug in the database query.",
            "because the customer has moved several states away and was not successfully transfered between regions."
        ]
    ),
    (
        "They can't issue a discount to a customer ",
        [
            "because they do not have the authority to do so.",
            "because a previous discount is under audit.",
            "because they are over their budget this month.",
            "because they incorrectly entered the authorization code."
        ]
    ),
    (
        "They can't access the sales pipeline ",
        [
            "because things happened in the wrong order during an employee termination.",
            "because there was a delay in their onboarding and they aren't associated with a dealership yet.",
            "because they were accidentally associated with another dealership.",
            "because they used to be employed at another location, but their account hasn't been updated to reflect their new location."
        ]
    ),
    (
        "They can't order more supply from manufacturing ",
        [
            "because the window for this month has closed and the next order window hasn't opened yet.",
            "they don't have the authority to order on their location's behalf.",
            "the database is down, orders can't be added, and the error messages are not being displayed.",
            "what they're trying to order has been discontinued."
        ]
    ),
    (
        "They can't check on the status of an order ",
        [
            "because they didn't enter the information correctly.",
            "because the order was not correctly added to the database.",
            "becasue their checking on someone else's order, and lack the authority to see it.",
            "because the order is too far in the past.",
            "because the database is unresponsive because of a cloud issue."
        ]
    ),
    (
        "They can't progress a customer in their sales pipeline ",
        [
            "because they're in their probation period and require a manager's approval to move them forward.",
            "there was no recorded interaction to justify the move in the pipeline.",
            "they're having trouble at a previous step, finding the customer in their pipeline."
        ]
    )
]

mechanic_issues = [
    (
        "They can't order a part ",
        [
            "the part is no longer in production and we are out of stock.",
            "they misentered the part number.",
            "they asked for a suspiciously large quantity and an audit is happening.",
            "they are in an ITAR controlled country and we cannot ship the parts to them.",
            "they have an outstanding invoice that needs to be resolved first."
        ]
    ),
    (
        "They can't enter maintenance data on a vehicle they're servicing ",
        [
            "because they entered the VIN wrong.",
            "because the data they've entered is inconsistent.",
            "because the backing database is not working.",
            "because they entered incorrect data.",
            "because the vehicle they're maintaining isn't part of our database."
        ]
    ),
    (
        "They can't find the maintenance history on a vehicle they're servicing ",
        [
            "because they entered the vehicle information incorrectly.",
            "because the vehicle being maintained isn't one of ours.",
            "because the database isn't available right now.",
            "because they lack authority to see our maintenance history database.",
        ]
    ),
    (
        "They can't find the customer whose vehicle they're working on ",
        [
            "because the vehicle was sold on the secondary market and our database was not updated.",
            "because the customer's name has changed due to marriage.",
            "because they entered the wrong vehicle information, and found a similar make and model belonging to another user."
        ]
    ),
    (
        "They can't mark a repair as complete ",
        [
            "because they haven't run a system diagnostic after the maintenance has been completed.",
            "because they are in a probationary period and need manager authorization to do so.",
            "because the steps they took do not rehabiltate the listed issues with the vehicle.",
            "because the post-repair diagnostic shows there is still a problem."
        ]
    )

]

manufacturer_issues = [
    (
        "They can't add a new part to the database ",
        [
            "because it was rejected due to a quality check (the part description has a spelling mistake in it).",
            "because the vehicle to which the part belongs was not added into the database first.",
            "because they lack the authority to add a new part to the database.",
            "because the database is currently down."
        ]
    ),
    (
        "They can't add a vehicle to the database ",
        [
            "because they lack the authority to add a new vehicle to the database.",
            "because the database is currently unavailable.",
            "because the new entry fails a quality check.",
            "because the vehicle already exists in the database, but the error message is unclear."
        ]
    ),
    (
        "They can't fulfill an order for a dealership, but they also can't decline that order ",
        [
            "because they lack the authority to turn down an order.",
            "because they have entered information incorrectly."
        ]
    ),
    (
        "They can't mark an order for a dealership as shipped ",
        [
            "because they lack the correct authorization.",
            "because their job title and responsibilities changed per HR, but the database hasn't been updated to reflect that.",
            "because the order has already been marked as shipped.",
            "because the database is unavailable right now."
        ]
    )
]

specific_issues = {
    "customer" : customer_issues,
    "salesperson" : salesperson_issues,
    "mechanic" : mechanic_issues,
    "manufacturer" : manufacturer_issues,
}

tail = "Please separate all emails in the chain with multiple line breaks and a line containing three hyphens."


def build_dataset(generator, cutoff=1):
    for base, specific_modifier in specific_modifiers.items():
        persona = generator.build_custom_personae(base, specific_modifier)
        queries = generator.generate_queries(specific_issues[base], persona)
        generator.get_queries(queries, cutoff)

data_location = "data/helpdesk.json"

def add_to_dataset():
    prev_run_as_path = Path(data_location)
    requester = lambda value, base, issue, reason: f"Please find me an email chain between IT and a {value} where the {base} is experiencing a situation like the following: {issue} {reason}"
    generator = None
    if prev_run_as_path.exists():
        generator = DatasetGenerator.load(data_location)
        generator.request_gen = requester
        print("Adding to previous run")
    else:
        generator = DatasetGenerator(common_issues, all_modifiers, preamble, tail, requester, output_path=data_location)
    build_dataset(generator, cutoff=None)
    generator.save(data_location)
    generator.display()
