"""
ANZA OPTION ANALYSIS - Main Entry Point
Production-ready, self-learning options analysis system
"""

import asyncio
import logging
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Import core modules
from core.data_fetcher import DataFetcher
from core.analyzers import GreeksAnalyzer, GEXAnalyzer, OIAnalyzer, SmartMoneyAnalyzer
from core.signal_generator import SignalGenerator
from core.knowledge_base import KnowledgeBase
from core.validator import MultiLevelValidator
from core.learner import SelfLearningEngine
from core.error_detector import ErrorDetectionSystem
from database.manager import DatabaseManager
from services.angel_one import AngelOneService
from services.alert_service import AlertService
from utils.logger import setup_logging
from config import settings

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class ANZAOptionsAnalyzer:
    """
    Main orchestrator for the entire system
    Combines all components into cohesive analysis engine
    """

    def __init__(self):
        logger.info("🚀 Initializing ANZA Options Analyzer...")

        # Initialize services
        self.angel_service = AngelOneService()
        self.alert_service = AlertService()
        self.db_manager = DatabaseManager()

        # Initialize data layer
        self.data_fetcher = DataFetcher(self.angel_service)

        # Initialize analysis components
        self.greeks_analyzer = GreeksAnalyzer()
        self.gex_analyzer = GEXAnalyzer()
        self.oi_analyzer = OIAnalyzer()
        self.smart_money_analyzer = SmartMoneyAnalyzer()
        self.signal_generator = SignalGenerator()

        # Initialize intelligence layer
        self.knowledge_base = KnowledgeBase()
        self.validator = MultiLevelValidator(self.knowledge_base)
        self.learner = SelfLearningEngine(self.db_manager)
        self.error_detector = ErrorDetectionSystem()

        # State management
        self.analysis_cycle = 0
        self.last_successful_analysis = None
        self.current_signals = []

        logger.info("✅ System initialized successfully")

    async def start(self):
        """
        Main entry point - starts the continuous analysis loop
        """
        logger.info("="*80)
        logger.info("🎯 ANZA OPTIONS ANALYZER STARTING")
        logger.info("="*80)

        # Login to Angel One
        try:
            # Check validation
            missing = settings.validate()
            if missing:
                logger.error(f"❌ Missing credentials: {missing}")
                return

            await self.angel_service.login()
            logger.info("✅ Angel One API connected")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Angel One: {e}")
            # return # Continue for simulation/demo if requested, but production should return

        # Test database connection
        if not self.db_manager.test_connection():
            logger.error("❌ Database connection failed")
            return

        logger.info("✅ Database connected")
        logger.info("🔄 Starting analysis loop (60-second intervals)")
        logger.info("-"*80)

        # Start main loop
        await self.run_continuous_analysis()

    async def run_continuous_analysis(self):
        """
        Runs analysis every 60 seconds
        This is the heart of the system
        """
        while True:
            self.analysis_cycle += 1
            cycle_start_time = datetime.now()

            try:
                logger.info(f"\n{'='*80}")
                logger.info(f"📊 ANALYSIS CYCLE #{self.analysis_cycle} - {cycle_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'='*80}\n")

                # ===== STEP 1: SYSTEM HEALTH CHECK =====
                logger.info("🔍 Step 1: Running system health check...")
                system_health = self.error_detector.check_all_systems()

                if not system_health['healthy']:
                    logger.warning(f"⚠️ System health issues detected:")
                    for error in system_health['errors']:
                        logger.warning(f"  - {error['severity']}: {error['message']}")

                    if self.error_detector.circuit_breaker_active:
                        logger.critical("🚨 CIRCUIT BREAKER ACTIVE - Skipping analysis")
                        await asyncio.sleep(60)
                        continue

                logger.info("✅ System health check passed\n")

                # ===== STEP 2: FETCH DATA =====
                logger.info("📥 Step 2: Fetching market data...")
                market_data = await self.data_fetcher.fetch_all_data()

                if not market_data:
                    logger.error("❌ Failed to fetch market data")
                    await asyncio.sleep(60)
                    continue

                logger.info(f"✅ Data fetched - NIFTY spot: {market_data['spot_price']:.2f}\n")

                # ===== STEP 3: DATA QUALITY CHECK =====
                logger.info("🔬 Step 3: Validating data quality...")
                data_quality = self.error_detector.validate_data_quality(market_data)

                if not data_quality['passed']:
                    logger.error(f"❌ Data quality issues: {data_quality['message']}")
                    await asyncio.sleep(60)
                    continue

                logger.info("✅ Data quality validated\n")

                # ===== STEP 4: RUN ANALYSES =====
                logger.info("🧮 Step 4: Running comprehensive analysis...")

                # Greeks analysis
                logger.info("  • Calculating Greeks...")
                greeks_results = self.greeks_analyzer.analyze(market_data)

                # GEX analysis
                logger.info("  • Calculating GEX...")
                gex_results = self.gex_analyzer.analyze(market_data, greeks_results)
                logger.info(f"    ✓ Net GEX: {gex_results['net_gex']/1e9:.2f}B ({gex_results['regime']})")

                # OI analysis
                logger.info("  • Analyzing Open Interest...")
                oi_results = self.oi_analyzer.analyze(market_data)
                logger.info(f"    ✓ PCR: {oi_results['pcr']:.3f}")

                # Smart Money analysis
                logger.info("  • Tracking Smart Money...")
                smart_money_results = self.smart_money_analyzer.analyze(market_data)

                logger.info("✅ Analysis complete\n")

                # ===== STEP 5: PATTERN MATCHING =====
                logger.info("🎯 Step 5: Matching patterns from knowledge base...")

                analysis_results = {
                    'market_data': market_data,
                    'greeks': greeks_results,
                    'gex': gex_results,
                    'oi': oi_results,
                    'smart_money': smart_money_results
                }

                matched_patterns = self.knowledge_base.find_matching_patterns(analysis_results)

                logger.info(f"✅ Found {len(matched_patterns)} matching patterns\n")

                # ===== STEP 6: GENERATE SIGNALS =====
                logger.info("💡 Step 6: Generating trade signals...")

                preliminary_signals = self.signal_generator.generate_signals(
                    analysis_results,
                    matched_patterns
                )

                logger.info(f"✅ Generated {len(preliminary_signals)} preliminary signals\n")

                # ===== STEP 7: MULTI-LEVEL VALIDATION =====
                logger.info("✔️ Step 7: Validating signals through multiple layers...")

                validated_signals = []
                for signal in preliminary_signals:
                    validation_result = self.validator.validate_signal(signal, analysis_results)

                    if validation_result['decision'] == 'APPROVED':
                        # Check for known failure scenarios
                        failure_check = self.knowledge_base.check_failure_scenarios(
                            signal, analysis_results
                        )

                        if failure_check.get('warnings'):
                            signal['warnings'] = failure_check['warnings']
                            signal['confidence'] -= 20

                        validated_signals.append(signal)

                logger.info(f"✅ {len(validated_signals)} signals passed validation\n")

                # ===== STEP 8: FINAL SIGNALS =====
                self.current_signals = validated_signals

                if validated_signals:
                    logger.info("🎯 FINAL TRADE SIGNALS:")
                    logger.info("="*80)

                    for idx, signal in enumerate(validated_signals, 1):
                        logger.info(f"\n{idx}. {signal['strategy'].upper()}")
                        logger.info(f"   Direction: {signal['direction']}")
                        logger.info(f"   Confidence: {signal['confidence']}%")
                        logger.info(f"   Entry: {signal['entry']}")
                        logger.info(f"   Reasoning: {signal['reasoning']}")

                    logger.info("\n" + "="*80)

                    # Send alerts
                    await self.alert_service.send_signals(validated_signals)

                else:
                    logger.info("⏸️ No signals generated - WAIT for better opportunities")

                # ===== STEP 9: SAVE TO DATABASE =====
                logger.info("\n💾 Step 9: Saving analysis to database...")

                self.db_manager.save_analysis_cycle(
                    cycle_number=self.analysis_cycle,
                    timestamp=cycle_start_time,
                    market_data=market_data,
                    analysis_results=analysis_results,
                    signals=validated_signals
                )

                logger.info("✅ Analysis saved\n")

                # ===== STEP 10: LEARNING =====
                if self.analysis_cycle % 10 == 0:
                    logger.info("📚 Step 10: Checking learning progress...")
                    report = self.learner.generate_performance_report()
                    logger.info(f"   Current Win Rate: {report['overall_win_rate']*100:.1f}%")

                # Mark as successful
                self.last_successful_analysis = datetime.now()
                self.db_manager.set_config("engine_running", "ON")

                cycle_duration = (datetime.now() - cycle_start_time).total_seconds()
                wait_time = max(0, 60 - cycle_duration)
                await asyncio.sleep(wait_time)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.exception(f"❌ Error in analysis cycle: {e}")
                await asyncio.sleep(60)

        await self.shutdown()

    async def shutdown(self):
        logger.info("🧹 Cleaning up...")
        self.angel_service.close()
        self.db_manager.close()
        self.db_manager.set_config("engine_running", "OFF")
        logger.info("\n✅ Shutdown complete.")


async def main():
    analyzer = ANZAOptionsAnalyzer()
    await analyzer.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
