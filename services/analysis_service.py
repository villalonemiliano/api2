from models.analysis import Analysis
import logging

logger = logging.getLogger(__name__)

class AnalysisService:
    @staticmethod
    def get_stock_analysis(symbol, available_fields):
        """
        Get and format stock analysis data
        """
        try:
            # Get latest analysis
            analysis_data = Analysis.get_latest_analysis(symbol)
            if not analysis_data:
                return None
            
            # Format response according to available fields
            return Analysis.format_analysis_response(analysis_data, available_fields)
        except Exception as e:
            logger.error(f"Error getting stock analysis: {str(e)}")
            raise 