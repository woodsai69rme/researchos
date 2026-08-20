"""
Unit Tests for Automotive XR6T / TH400 Compatibility Engine
"""
from researchos.packages.business.automotive import AutomotiveKnowledgeEngine


def test_automotive_engine_identifies_barra_th400():
    engine = AutomotiveKnowledgeEngine()
    specs = engine.verify_compatibility("Find a complete 1,000hp Ford Falcon XR6 Turbo TH400 setup in Queensland")

    assert specs["fitment_status"] == "Compatible with Conversion Kit"
    assert specs["engine_platform"] == "Ford 4.0L DOHC Barra I6 Turbo"
    assert specs["transmission"] == "GM TH400 3-Speed Automatic"
    assert "gearbox" in specs["component_breakdown"]
    assert "bellhousing" in specs["component_breakdown"]
    assert "tailshaft" in specs["component_breakdown"]
    assert len(specs["recommended_workshops"]) >= 3
