# csp_yield.py
# From Classic Computer Science Problems in Python Chapter 3
# Copyright 2018 David Kopec
#
# Modified by Russ Abbott (July 2019)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Generic, Dict, List, Optional, Set, TypeVar

from csp import Constraint, select_next_var

V = TypeVar('V')  # variable type
D = TypeVar('D')  # domain type


# A constraint satisfaction problem consists of variables of type V
# that have ranges of values known as domains of type D and constraints
# that determine whether a particular variable's domain selection is valid
class CSP(Generic[V, D]):
    def __init__(self, variables: List[V], domains: Dict[V, Set[D]]) -> None:
        self.variables: List[V] = variables  # variables to be constrained
        self.domains: Dict[V, Set[D]] = domains  # domain of each variable
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        self.low_mark = len(variables)
        self.count = 0
        for variable in self.variables:
            self.constraints[variable] = []
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it.")

    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)

    # noinspection PyDefaultArgument
    def backtracking_search(self, assignment: Dict[V, D], unassigned: Dict[V, Set[D]],
                            search_strategy='ff',
                            propagate_constraints=True,
                            order_domain=True,
                            check_constraints=False) -> Optional[Dict[V, D]]:
        # assignment is complete there are no unassigned variables left
        first_solution = True
        if not unassigned:
            first_solution = False
            yield assignment

        else:
            if first_solution:
                # Print progress if at or below low-water mark.
                nbr_left = len(unassigned)
                if nbr_left <= self.low_mark:
                    self.count += 1
                    print(nbr_left, end='\n' if self.count % 20 == 0 else ' ')
                    self.low_mark = nbr_left

            # select the variable to assign next.
            (next_var, next_var_domain) = select_next_var(search_strategy, order_domain, unassigned)
            for value in next_var_domain:
                extended_assignment = assignment.copy( )
                extended_assignment[next_var] = value
                next_unassigned = unassigned
                if propagate_constraints:
                    for constraint in self.constraints[next_var]:
                        # next_unassigned will be None if some domain is empty.
                        next_unassigned = constraint.propagate(next_var, value, next_unassigned)
                # if we're still consistent, we recurse (continue)
                if next_unassigned and not check_constraints or self.consistent(next_var, extended_assignment):
                    for result in self.backtracking_search(extended_assignment, next_unassigned,
                                                           search_strategy=search_strategy,
                                                           propagate_constraints=propagate_constraints,
                                                           order_domain=order_domain,
                                                           check_constraints=check_constraints):
                        # if we didn't find the result, we will end up backtracking
                        if result is not None:
                            yield result
            return None

    # Check if the value assignment is consistent by checking all constraints for the given variable against it.
    # May not need this if we propagate_constraints. Then only consistent values remain in the domains.
    # But might there be constraints that are not caught that way?
    def consistent(self, variable: V, assignment: Dict[V, D]) -> bool:
        for constraint in self.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True
