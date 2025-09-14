from config import WIDTH, HEIGHT

class CSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables 
        self.domains = domains      
        self.constraints = constraints 

    def is_consistent(self, variable, assignment):
        # Check if the current assignment is consistent with the constraints
        for constraint in self.constraints:
            if not constraint(assignment):
                return False
        return True

    def backtrack(self, assignment):
        if len(assignment) == len(self.variables):
            return assignment  # All variables are assigned

        # Select the next variable to assign
        unassigned = [v for v in self.variables if v not in assignment]
        variable = unassigned[0]

        for value in self.domains[variable]:
            assignment[variable] = value
            if self.is_consistent(variable, assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
            del assignment[variable]  # Remove the assignment if it fails

        return None  # No valid assignment found
    
def within_bounds_constraint(assignment):
    for position in assignment.values():
        x, y = position
        if x < 0 or x > WIDTH or y < 0 or y > HEIGHT:
            return False  # Position is out of bounds
    return True  # All positions are within bounds
    
def no_overlap_constraint(assignment):
    positions = list(assignment.values())
    return len(positions) == len(set(positions))  # Ensure all positions are unique