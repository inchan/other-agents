"""MCP 프로토콜 준수 테스트

MCP 서버가 Model Context Protocol 스펙을 올바르게 구현하는지 검증합니다.
"""

import pytest
from other_agents_mcp.server import app, list_available_tools as list_tools, call_tool


class TestMCPServerInitialization:
    """MCP 서버 초기화 테스트"""

    def test_server_instance_created(self):
        """서버 인스턴스가 생성되는지 확인"""
        assert app is not None
        assert hasattr(app, "name")

    def test_server_name(self):
        """서버 이름이 올바른지 확인"""
        assert app.name == "other-agents-mcp"


class TestListToolsHandler:
    """list_tools() 핸들러 테스트"""

    @pytest.mark.asyncio
    async def test_list_tools_returns_list(self):
        """list_tools()가 리스트를 반환하는지 확인"""
        tools = await list_tools()
        assert isinstance(tools, list)

    @pytest.mark.asyncio
    async def test_list_tools_count(self):
        """도구가 7개인지 확인 (list_agents, use_agent, use_agents, get_task_status, add_agent, start_meeting, get_meeting_status)"""
        tools = await list_tools()
        assert len(tools) == 7

    @pytest.mark.asyncio
    async def test_list_tools_schema_structure(self):
        """각 도구가 필수 필드를 가지는지 확인"""
        tools = await list_tools()

        for tool in tools:
            # MCP 프로토콜 필수 필드
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")

            # 각 필드 타입 검증
            assert isinstance(tool.name, str)
            assert isinstance(tool.description, str)
            assert isinstance(tool.inputSchema, dict)

    @pytest.mark.asyncio
    async def test_list_tools_input_schema_valid(self):
        """inputSchema가 JSON Schema 형식인지 확인"""
        tools = await list_tools()

        for tool in tools:
            schema = tool.inputSchema

            # JSON Schema 필수 필드
            assert "type" in schema
            assert schema["type"] == "object"

            # properties 또는 빈 스키마
            if "properties" in schema:
                assert isinstance(schema["properties"], dict)

    @pytest.mark.asyncio
    async def test_list_tools_tool_definition(self):
        """list_tools 도구 정의 확인"""
        tools = await list_tools()
        list_clis_tool = next((t for t in tools if t.name == "list_agents"), None)

        assert list_clis_tool is not None
        assert "AI CLI" in list_clis_tool.description
        assert "claude" in list_clis_tool.description or "gemini" in list_clis_tool.description
        assert list_clis_tool.inputSchema["type"] == "object"
        # check_auth 파라미터가 있어야 함
        assert "check_auth" in list_clis_tool.inputSchema["properties"]

    @pytest.mark.asyncio
    async def test_run_tool_tool_definition(self):
        """run_tool 도구 정의 확인"""
        tools = await list_tools()
        run_tool_def = next((t for t in tools if t.name == "use_agent"), None)

        assert run_tool_def is not None
        assert "AI CLI" in run_tool_def.description
        assert "claude" in run_tool_def.description or "codex" in run_tool_def.description

        # inputSchema 검증
        schema = run_tool_def.inputSchema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema

        # properties 검증
        assert "cli_name" in schema["properties"]
        assert "message" in schema["properties"]
        assert "run_async" in schema["properties"]

        # required 필드 검증
        assert "cli_name" in schema["required"]
        assert "message" in schema["required"]

    @pytest.mark.asyncio
    async def test_get_run_status_tool_definition(self):
        """get_run_status 도구 정의 확인"""
        tools = await list_tools()
        status_tool = next((t for t in tools if t.name == "get_task_status"), None)

        assert status_tool is not None
        assert "비동기 실행" in status_tool.description
        assert "task_id" in status_tool.inputSchema["properties"]


class TestCallToolHandler:
    """call_tool() 핸들러 테스트"""

    @pytest.mark.asyncio
    async def test_call_tool_is_async(self):
        """call_tool이 async 함수인지 확인"""
        import inspect

        assert inspect.iscoroutinefunction(call_tool)

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self):
        """알 수 없는 도구 호출 시 에러 반환"""
        result = await call_tool("unknown_tool", {})

        assert "error" in result
        assert "Unknown tool" in result["error"]

    @pytest.mark.asyncio
    async def test_call_tool_returns_dict(self):
        """call_tool이 딕셔너리를 반환하는지 확인"""
        # list_tools는 항상 성공
        result = await call_tool("list_agents", {})
        assert isinstance(result, dict)


class TestMCPProtocolCompliance:
    """MCP 프로토콜 스펙 준수 테스트"""

    @pytest.mark.asyncio
    async def test_tool_names_are_valid(self):
        """도구 이름이 유효한 형식인지 확인 (소문자, 밑줄만)"""
        tools = await list_tools()

        for tool in tools:
            name = tool.name
            # MCP 권장사항: snake_case
            assert name.islower() or "_" in name
            assert " " not in name  # 공백 없음
            assert "-" not in name  # 하이픈 사용 안 함 (밑줄 사용)

    @pytest.mark.asyncio
    async def test_tool_descriptions_are_informative(self):
        """도구 설명이 충분한 정보를 제공하는지 확인"""
        tools = await list_tools()

        for tool in tools:
            description = tool.description
            # 최소 10자 이상의 설명
            assert len(description) >= 10
            # 한글 또는 영문 포함
            assert any(ord(c) > 127 or c.isalpha() for c in description)

    @pytest.mark.asyncio
    async def test_input_schema_has_correct_type(self):
        """모든 inputSchema의 type이 'object'인지 확인"""
        tools = await list_tools()

        for tool in tools:
            assert tool.inputSchema["type"] == "object"

    @pytest.mark.asyncio
    async def test_required_fields_are_in_properties(self):
        """required에 명시된 필드가 properties에 존재하는지 확인"""
        tools = await list_tools()

        for tool in tools:
            schema = tool.inputSchema

            if "required" in schema:
                required_fields = schema["required"]
                properties = schema.get("properties", {})

                for field in required_fields:
                    assert (
                        field in properties
                    ), f"Required field '{field}' not found in properties of {tool.name}"


class TestErrorResponseFormat:
    """에러 응답 형식 테스트"""

    @pytest.mark.asyncio
    async def test_unknown_tool_error_format(self):
        """알 수 없는 도구 에러 응답 형식 검증"""
        result = await call_tool("nonexistent_tool", {})

        # 에러 필드 존재 확인
        assert "error" in result
        assert isinstance(result["error"], str)
        assert len(result["error"]) > 0

    @pytest.mark.asyncio
    async def test_error_message_is_descriptive(self):
        """에러 메시지가 설명적인지 확인"""
        result = await call_tool("invalid_tool_name", {})

        assert "error" in result
        # 도구 이름이 에러 메시지에 포함되어야 함
        assert "invalid_tool_name" in result["error"] or "Unknown" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
