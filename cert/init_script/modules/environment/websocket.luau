local WebSocket = {}

function WebSocket.connect(url)
    -- Simulated WebSocket object
    local ws = {}
    
    -- Simulated methods
    function ws:Send(message)
        -- Simulated Send function
    end
    
    function ws:Close()
        -- Simulated Close function
    end
    
    -- Simulated event properties
    ws.OnMessage = {}
    ws.OnClose = {}
    
    -- Return the simulated WebSocket object
    return ws
end

return function()
    return {
        ["WebSocket"] = WebSocket,
        ["websocket"] = WebSocket,
    }
end