-- Random Replacement strategy
--
-- Keys used in GET/SET are added to a zset _RR_::<namsepace> with score set to 1.
-- When set is over capacity an element is removed by given random rank and the
-- corresponding key is deleted from the database.

local command = ARGV[1]
local replace = ARGV[2]
local rr_key = "_RR_::" .. ARGV[3]
local max_entries = ARGV[4]
local ct, rval, to_remove

-- GET or SET the key

if command == 'GET' then
    rval = redis.call('GET', KEYS[1])
else
    redis.call('SET', KEYS[1], ARGV[5])
    rval = true
end

if rval == nil then
    return
end

redis.call('ZADD', rr_key, 1, KEYS[1])
ct = redis.call('ZCARD', rr_key)
if ct == (max_entries + 1) then
    print('removing ct=' .. ct .. ' replace=' .. replace)
    to_remove = redis.call('ZRANGE', rr_key, replace, replace)
    print('to_remove=' .. to_remove[1])
    redis.call('ZREM', rr_key, to_remove[1])
    redis.call('DEL', to_remove[1])
end

return rval
