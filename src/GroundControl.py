from streamlit_app import main as start_streamlit_app

class GroundControl(object):
    """Singleton object representing our ground control station"""
        
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.UAV = None
                
    def host_streamlit(self):
        start_streamlit_app()
        
    
        
if __name__ == "__main__":
    
    pass