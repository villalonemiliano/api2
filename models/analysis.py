from database.connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

class Analysis:
    @staticmethod
    def get_latest_analysis(symbol):
        """
        Get the latest analysis for a given stock symbol
        """
        try:
            with get_db_connection('analysis') as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT symbol, timestamp, price, 
                           short_term, short_score,
                           medium_term, medium_score,
                           long_term, long_score,
                           fund_score
                    FROM analysis 
                    WHERE symbol = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                '''
                result = cursor.execute(query, (symbol.upper(),)).fetchone()
                
                if not result:
                    return None
                
                return dict(result)
        except Exception as e:
            logger.error(f"Error getting analysis for {symbol}: {str(e)}")
            raise

    @staticmethod
    def format_analysis_response(analysis_data, available_fields):
        """
        Format the analysis data according to the user's plan
        """
        if not analysis_data:
            return None

        response = {
            "symbol": analysis_data['symbol'],
            "timestamp": analysis_data['timestamp'],
            "classifications": {
                "short_term": {
                    "classification": analysis_data['short_term'],
                    "score": analysis_data['short_score']
                },
                "medium_term": {
                    "classification": analysis_data['medium_term'],
                    "score": analysis_data['medium_score']
                },
                "long_term": {
                    "classification": analysis_data['long_term'],
                    "score": analysis_data['long_score']
                }
            }
        }

        # Add additional fields based on plan
        if 'fund_score' in available_fields or available_fields == 'all':
            response["fundamental_score"] = analysis_data['fund_score']
            
        if 'price_data' in available_fields or available_fields == 'all':
            response["price"] = analysis_data['price']

        return response 