"""Test the condition decorators."""
# pylint: disable=protected-access,import-error
import asyncio
from datetime import timedelta
from unittest.mock import patch

import pytest

from supervisor.const import CoreState
from supervisor.coresys import CoreSys
from supervisor.exceptions import HassioError, JobException
from supervisor.jobs.const import JobExecutionLimit
from supervisor.jobs.decorator import Job, JobCondition
from supervisor.resolution.const import UnhealthyReason


async def test_healthy(coresys: CoreSys):
    """Test the healty decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.HEALTHY])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    assert await test.execute()

    coresys.resolution.unhealthy = UnhealthyReason.DOCKER
    assert not await test.execute()


async def test_internet(coresys: CoreSys):
    """Test the internet decorator."""
    coresys.core.state = CoreState.RUNNING

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.INTERNET_HOST])
        async def execute_host(self):
            """Execute the class method."""
            return True

        @Job(conditions=[JobCondition.INTERNET_SYSTEM])
        async def execute_system(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)

    coresys.host.network._connectivity = True
    coresys.supervisor._connectivity = True
    assert await test.execute_host()
    assert await test.execute_system()

    coresys.host.network._connectivity = True
    coresys.supervisor._connectivity = False
    assert await test.execute_host()
    assert not await test.execute_system()

    coresys.host.network._connectivity = None
    coresys.supervisor._connectivity = True
    assert await test.execute_host()
    assert await test.execute_system()

    coresys.host.network._connectivity = False
    coresys.supervisor._connectivity = True
    assert not await test.execute_host()
    assert await test.execute_system()


async def test_free_space(coresys: CoreSys):
    """Test the free_space decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.FREE_SPACE])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    with patch("shutil.disk_usage", return_value=(42, 42, (1024.0 ** 3))):
        assert await test.execute()

    with patch("shutil.disk_usage", return_value=(42, 42, (512.0 ** 3))):
        assert not await test.execute()


async def test_haos(coresys: CoreSys):
    """Test the haos decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.HAOS])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    coresys.hassos._available = True
    assert await test.execute()

    coresys.hassos._available = False
    assert not await test.execute()


async def test_internet_connectivity_with_core_state(coresys: CoreSys):
    """Test the different core states and the impact for internet condition."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.INTERNET_SYSTEM, JobCondition.INTERNET_HOST])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)
    coresys.host.network._connectivity = False
    coresys.supervisor._connectivity = False

    coresys.core.state = CoreState.INITIALIZE
    assert await test.execute()

    coresys.core.state = CoreState.SETUP
    assert not await test.execute()

    coresys.core.state = CoreState.STARTUP
    assert await test.execute()

    coresys.core.state = CoreState.RUNNING
    assert not await test.execute()

    coresys.core.state = CoreState.CLOSE
    assert await test.execute()

    coresys.core.state = CoreState.SHUTDOWN
    assert await test.execute()

    coresys.core.state = CoreState.STOPPING
    assert await test.execute()


async def test_exception(coresys: CoreSys):
    """Test the healty decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.HEALTHY])
        async def execute(self):
            """Execute the class method."""
            raise HassioError()

    test = TestClass(coresys)

    with pytest.raises(HassioError):
        assert await test.execute()


async def test_exception_not_handle(coresys: CoreSys):
    """Test the healty decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.HEALTHY])
        async def execute(self):
            """Execute the class method."""
            raise Exception()

    test = TestClass(coresys)

    with pytest.raises(JobException):
        assert await test.execute()


async def test_running(coresys: CoreSys):
    """Test the running decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.RUNNING])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)

    coresys.core.state = CoreState.RUNNING
    assert await test.execute()

    coresys.core.state = CoreState.FREEZE
    assert not await test.execute()


async def test_ignore_conditions(coresys: CoreSys):
    """Test the ignore conditions decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.RUNNING])
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)

    coresys.core.state = CoreState.RUNNING
    assert await test.execute()

    coresys.core.state = CoreState.FREEZE
    assert not await test.execute()

    coresys.jobs.ignore_conditions = [JobCondition.RUNNING]
    assert await test.execute()


async def test_exception_conditions(coresys: CoreSys):
    """Test the ignore conditions decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys

        @Job(conditions=[JobCondition.RUNNING], on_condition=HassioError)
        async def execute(self):
            """Execute the class method."""
            return True

    test = TestClass(coresys)

    coresys.core.state = CoreState.RUNNING
    assert await test.execute()

    coresys.core.state = CoreState.FREEZE
    with pytest.raises(HassioError):
        await test.execute()


async def test_exectution_limit_single_wait(
    coresys: CoreSys, loop: asyncio.BaseEventLoop
):
    """Test the ignore conditions decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()

        @Job(limit=JobExecutionLimit.SINGLE_WAIT)
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)

    test = TestClass(coresys)

    await asyncio.gather(*[test.execute(0.1), test.execute(0.1), test.execute(0.1)])


async def test_exectution_limit_throttle_wait(
    coresys: CoreSys, loop: asyncio.BaseEventLoop
):
    """Test the ignore conditions decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(limit=JobExecutionLimit.THROTTLE_WAIT, throttle_period=timedelta(hours=1))
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)
            self.call += 1

    test = TestClass(coresys)

    await asyncio.gather(*[test.execute(0.1), test.execute(0.1), test.execute(0.1)])
    assert test.call == 1

    await asyncio.gather(*[test.execute(0.1)])
    assert test.call == 1


async def test_exectution_limit_throttle(coresys: CoreSys, loop: asyncio.BaseEventLoop):
    """Test the ignore conditions decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()
            self.call = 0

        @Job(limit=JobExecutionLimit.THROTTLE, throttle_period=timedelta(hours=1))
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)
            self.call += 1

    test = TestClass(coresys)

    await asyncio.gather(*[test.execute(0.1), test.execute(0.1), test.execute(0.1)])
    assert test.call == 1

    await asyncio.gather(*[test.execute(0.1)])
    assert test.call == 1


async def test_exectution_limit_once(coresys: CoreSys, loop: asyncio.BaseEventLoop):
    """Test the ignore conditions decorator."""

    class TestClass:
        """Test class."""

        def __init__(self, coresys: CoreSys):
            """Initialize the test class."""
            self.coresys = coresys
            self.run = asyncio.Lock()

        @Job(limit=JobExecutionLimit.ONCE, on_condition=JobException)
        async def execute(self, sleep: float):
            """Execute the class method."""
            assert not self.run.locked()
            async with self.run:
                await asyncio.sleep(sleep)

    test = TestClass(coresys)
    run_task = loop.create_task(test.execute(0.3))

    await asyncio.sleep(0.1)
    with pytest.raises(JobException):
        await test.execute(0.1)

    await run_task
