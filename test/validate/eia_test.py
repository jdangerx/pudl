"""Validate post-ETL EIA 860 data and the associated derived outputs."""
import logging
from test.conftest import skip_table_if_null_freq_table

import pytest

from pudl import validate as pv
from pudl.output.pudltabl import PudlTabl

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "df_name,cols",
    [
        ("bf_eia923", "all"),
        ("bga_eia860", "all"),
        ("frc_eia923", "all"),
        ("gen_eia923", "all"),
        ("gens_eia860", "all"),
        ("gf_eia923", "all"),
        ("gf_nonuclear_eia923", "all"),
        ("gf_nuclear_eia923", "all"),
        ("own_eia860", "all"),
        ("plants_eia860", "all"),
        ("pu_eia860", "all"),
        ("utils_eia860", "all"),
    ],
)
def test_no_null_cols_eia(pudl_out_eia, live_dbs, cols, df_name):
    """Verify that output DataFrames have no entirely NULL columns."""
    if not live_dbs:
        pytest.skip("Data validation only works with a live PUDL DB.")
    skip_table_if_null_freq_table(table_name=df_name, freq=pudl_out_eia.freq)
    pv.no_null_cols(
        pudl_out_eia.__getattribute__(df_name)(), cols=cols, df_name=df_name
    )


@pytest.mark.parametrize(
    "df_name,raw_rows,monthly_rows,annual_rows",
    [
        ("bf_eia923", 1_415_232, 1_415_232, 118_550),
        ("bga_eia860", 129_869, 129_869, 129_869),
        ("frc_eia923", 596_855, 244_403, 24_064),
        ("gen_eia923", None, 5_170_743, 432_542),
        ("gens_eia860", 523_343, 523_343, 523_343),
        ("gf_eia923", 2_687_321, 2_687_321, 230_147),
        ("gf_nonuclear_eia923", 2_671_268, 2_671_268, 228_804),
        ("gf_nuclear_eia923", 24_617, 24_617, 2_058),
        ("own_eia860", 84_440, 84_440, 84_440),
        ("plants_eia860", 185_357, 185_357, 185_357),
        ("pu_eia860", 184_546, 184_546, 184_546),
        ("utils_eia860", 119_277, 119_277, 119_277),
    ],
)
def test_minmax_rows(
    pudl_out_eia: PudlTabl,
    live_dbs: bool,
    raw_rows: int | None,
    annual_rows: int,
    monthly_rows: int,
    df_name: str,
):
    """Verify that output DataFrames don't have too many or too few rows.

    Args:
        pudl_out_eia: A PudlTabl output object.
        live_dbs (bool): Whether we're using a live or testing DB.
        raw_rows: The expected original number of rows, without aggregation.
        annual_rows: The expected number of rows when using annual aggregation.
        monthly_rows: The expected number of rows when using monthly aggregation.
        df_name (str): Shorthand name identifying the dataframe, corresponding
            to the name of the function used to pull it from the PudlTabl
            output object.
    """
    if not live_dbs:
        pytest.skip("Data validation only works with a live PUDL DB.")
    skip_table_if_null_freq_table(table_name=df_name, freq=pudl_out_eia.freq)
    if pudl_out_eia.freq == "AS":
        expected_rows = annual_rows
    elif pudl_out_eia.freq == "MS":
        expected_rows = monthly_rows
    else:
        assert pudl_out_eia.freq is None
        expected_rows = raw_rows

    _ = (
        pudl_out_eia.__getattribute__(df_name)()
        .pipe(
            pv.check_min_rows, expected_rows=expected_rows, margin=0.0, df_name=df_name
        )
        .pipe(
            pv.check_max_rows, expected_rows=expected_rows, margin=0.0, df_name=df_name
        )
    )


@pytest.mark.parametrize(
    "df_name,unique_subset",
    [
        (
            "bf_eia923",
            [
                "report_date",
                "plant_id_eia",
                "boiler_id",
                "energy_source_code",
            ],
        ),
        ("bga_eia860", ["report_date", "plant_id_eia", "boiler_id", "generator_id"]),
        ("gen_eia923", ["report_date", "plant_id_eia", "generator_id"]),
        ("gens_eia860", ["report_date", "plant_id_eia", "generator_id"]),
        (
            "gf_eia923",
            ["report_date", "plant_id_eia", "prime_mover_code", "energy_source_code"],
        ),
        (
            "gf_nonuclear_eia923",
            ["report_date", "plant_id_eia", "prime_mover_code", "energy_source_code"],
        ),
        (
            "gf_nuclear_eia923",
            [
                "report_date",
                "plant_id_eia",
                "nuclear_unit_id",
                "prime_mover_code",
                "energy_source_code",
            ],
        ),
        (
            "own_eia860",
            ["report_date", "plant_id_eia", "generator_id", "owner_utility_id_eia"],
        ),
        ("plants_eia860", ["report_date", "plant_id_eia"]),
        ("pu_eia860", ["report_date", "plant_id_eia"]),
        ("utils_eia860", ["report_date", "utility_id_eia"]),
    ],
)
def test_unique_rows_eia(pudl_out_eia, live_dbs, unique_subset, df_name):
    """Test whether dataframe has unique records within a subset of columns."""
    if not live_dbs:
        pytest.skip("Data validation only works with a live PUDL DB.")
    skip_table_if_null_freq_table(table_name=df_name, freq=pudl_out_eia.freq)
    pv.check_unique_rows(
        pudl_out_eia.__getattribute__(df_name)(), subset=unique_subset, df_name=df_name
    )
