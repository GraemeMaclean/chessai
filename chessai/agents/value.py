import math

import chessai.core.action
import chessai.core.agent
import chessai.core.gamestate

class ValueAgent(chessai.core.agent.Agent):
    """ An agent that takes an action that maximizes the value of the resulting board position. """

    def get_action(self,
            state: chessai.core.gamestate.GameState) -> chessai.core.action.Action:
        """
        Returns the action that maximizes the expected value of the resulting board.
        """

        # Start with a very bad value.
        best_score: float = -math.inf
        best_action: chessai.core.action.Action | None = None

        legal_actions = state.get_legal_actions()
        self.rng.shuffle(legal_actions)
        for action in legal_actions:
            curr_state = state.generate_successor(action)
            opponents_score = self.evaluate_state(curr_state)

            # The action score is the inverse of the resulting score for the opponent.
            action_score = -1 * opponents_score

            # Check if we should accept the current action based on the expected value of the state.
            if (action_score > best_score):
                best_score = action_score
                best_action = action

        if (best_action is not None):
            return best_action

        # If we couldn't find an action, return a random action.
        if (len(legal_actions) > 0):
            return legal_actions[0]

        return chessai.core.action.NULL_ACTION
