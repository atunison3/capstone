if __name__ == "__main__":
    print(
        """
Let's say Bob wants to take Alice to the school dance. Alice is very smart and athletic, Bob on the other hand... is not.

Bob assumes his probability of Alice saying yes is 1 in a million. If this is true, Bob has an odds of Alice saying yes as
(1 / 999,999).

Knowing these are weak odds, Bob decides to join a club or team to improve his odds. He figures that if he joins the football
team Alice cheers for, his probability of Alice saying yes would be 1000x. Also, if Bob joins the reading club Alice is in, his probability of
Alice saying yes would be 10,000x. However, if Bob joins both the football team and the reading club, she will probably notice Bob
following her and say no to any dance (a probability of 0*).

This can be represented using the following:

log odds = logit(β₀ + β₁X₁ + β₂X₂ + β₃X₁X₂)

where
    β₁: Baseline chance
    β₁: Effect of joining the football team
    β₂: Effect of joining the reading club
    β₃: Interaction effect of joining both the football team and reading club
    X₁: 1 if Bob joins the football team, 0 otherwise
    X₂: 1 if Bob joins the reading club, 0 otherwise
    X₁X₂: 1 if Bob joins both the football team and reading club, 0 otherwise

* Note: In logistic regression, there is still a chance. An actual probability of 0 would be (0 / (1 - 0)) which would be infinity
    """
    )
