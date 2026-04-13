import chessai.core.action
import chessai.core.agent
import chessai.core.gamestate

class AggressiveAgent(chessai.core.agent.Agent):
    """ An agent that just takes a stochastic agressive action. """

    def get_action(self,
            state: chessai.core.gamestate.GameState) -> chessai.core.action.Action:
        """
        Returns a stochastic aggressive action based on the game state.
        """

        legal_actions = state.get_legal_actions()
        self.rng.shuffle(legal_actions)
        for action in legal_actions:
            if (state.is_capture(action)):
                return action

        # If we couldn't find an action that is a capture, return a random action.
        if (len(legal_actions) > 0):
            return legal_actions[0]

        return chessai.core.action.NULL_ACTION
