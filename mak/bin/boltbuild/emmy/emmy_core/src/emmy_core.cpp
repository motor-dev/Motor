#include "emmy_debugger/debugger/emmy_debugger_lib.h"

extern "C" {

    int emmy_tcp_listen(lua_State* L)
    {
        return ::tcpListen(L);
    }

    int emmy_tcp_connect(lua_State* L)
    {
        return ::tcpConnect(L);
    }

    int emmy_wait_IDE(lua_State* L)
    {
        return ::waitIDE(L);
    }

    int emmy_break(lua_State* L)
    {
        return ::breakHere(L);
    }
}
