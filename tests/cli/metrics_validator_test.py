""" Tests for cli/metrics.py module """

from datetime import datetime

import pytest

from cli.metrics import validator
from core.metrics import get_metrics_from_events, get_nodes_for_validator
from tests.constants import D_VALIDATOR_ID, SERVICE_ROW_COUNT
from tests.prepare_data import set_test_msr
from utils.texts import Texts

pytestmark = pytest.mark.skipif(reason="skip temporary")
G_TEXTS = Texts()
NO_DATA_MSG = G_TEXTS['msg']['no_data']
NEG_ID_MSG = G_TEXTS['metrics']['validator']['index']['valid_id_msg']
NOT_EXIST_VAL_ID_MSG = G_TEXTS['metrics']['validator']['index']['id_error_msg']


def setup_module(module):
    set_test_msr(0)


def teardown_module(module):
    set_test_msr()


def yy_mm_dd_to_date(date_str):
    format_str = '%Y-%m-%d'
    return datetime.strptime(date_str, format_str)


def test_neg_id(runner):
    result = runner.invoke(validator, ['-id', str(-1)])
    output_list = result.output.splitlines()

    assert NEG_ID_MSG == output_list[-1]


def test_not_existing_id(runner):
    result = runner.invoke(validator, ['-id', str(10)])
    output_list = result.output.splitlines()
    assert NOT_EXIST_VAL_ID_MSG == output_list[-1]


def test_metrics(skale, runner):
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID)])
    node_ids = get_nodes_for_validator(skale, D_VALIDATOR_ID)
    metrics, total_bounty = get_metrics_from_events(skale, node_ids, is_validator=True)
    row_count = len(metrics) + SERVICE_ROW_COUNT
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert f'{metrics[1][0]}         {metrics[1][1]}    {metrics[1][2]:.1f}          {metrics[1][3]}       {metrics[1][4]:.1f}' == output_list[3]  # noqa
    assert f'{metrics[2][0]}         {metrics[2][1]}    {metrics[2][2]:.1f}          {metrics[2][3]}       {metrics[2][4]:.1f}' == output_list[4]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_limited(skale, runner):
    node_ids = get_nodes_for_validator(skale, D_VALIDATOR_ID)
    metrics, total_bounty = get_metrics_from_events(skale, node_ids, is_validator=True, limit=1)

    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1)])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_limited_not_empty(skale, runner):
    start_date = '2000-01-01'
    node_ids = get_nodes_for_validator(skale, D_VALIDATOR_ID)
    metrics, total_bounty = get_metrics_from_events(skale, node_ids, is_validator=True, limit=1,
                                                    start_date=yy_mm_dd_to_date(start_date))
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1), '-s', start_date])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_limited_empty(runner):
    start_date = '2100-01-01'
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1), '-s', start_date])
    output_list = result.output.splitlines()

    assert NO_DATA_MSG == output_list[-1]


def test_metrics_till_limited_not_empty(skale, runner):
    end_date = '2100-01-01'
    node_ids = get_nodes_for_validator(skale, D_VALIDATOR_ID)
    metrics, total_bounty = get_metrics_from_events(skale, node_ids, is_validator=True, limit=1,
                                                    end_date=yy_mm_dd_to_date(end_date))
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1), '-t', end_date])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_till_limited_empty(runner):
    end_date = '2000-01-01'
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1), '-t', end_date])
    output_list = result.output.splitlines()

    assert NO_DATA_MSG == output_list[-1]


def test_metrics_since_till_limited_not_empty(skale, runner):
    start_date = '2000-01-01'
    end_date = '2100-01-01'
    node_ids = get_nodes_for_validator(skale, D_VALIDATOR_ID)
    metrics, total_bounty = get_metrics_from_events(skale, node_ids, is_validator=True, limit=1,
                                                    start_date=yy_mm_dd_to_date(start_date),
                                                    end_date=yy_mm_dd_to_date(end_date))
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1),
                                       '-s', start_date, '-t', end_date])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_till_limited_empty(runner):
    start_date = '2100-01-01'
    end_date = '2100-02-01'
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1),
                                       '-s', start_date, '-t', end_date])
    output_list = result.output.splitlines()

    assert NO_DATA_MSG == output_list[-1]
