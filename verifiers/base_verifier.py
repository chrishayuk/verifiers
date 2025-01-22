# base_verifier.py
import abc

class BaseVerifier(abc.ABC):
    """
    Defines a standard interface for verifiers:
    - A 'verify' method that returns a float score in [0.0, 1.0].
    - A 'to_json' method describing parameters and usage for programmatic consumption.
    """
    
    def __init__(self, name: str, description: str, parameters: dict = None):
        """
        Parameters
        ----------
        name : str
            A short identifier for the verifier, e.g. "line_count_verifier"
        description : str
            A longer description for documentation.
        parameters : dict
            A dictionary describing parameters needed by the verifier, 
            their types, and default values, for example:
            
            {
              "desired": {
                "type": "integer",
                "default": 5,
                "description": "Desired line count"
              }
            }
        """
        self.name = name
        self.description = description
        self.parameters = parameters if parameters else {}
    
    @abc.abstractmethod
    def verify(self, text: str, **kwargs) -> float:
        """
        Evaluate 'text' and return a score in [0.0, 1.0].
        Child classes must implement this.
        """
        pass
    
    def to_json(self):
        """
        Returns a dictionary that can be JSON-serialized, describing
        what this verifier does and how to call it.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
