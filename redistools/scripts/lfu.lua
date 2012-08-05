-- LFU replacement strategy
--
-- Keys used in GET/SET are added to a zset _LFU_::<namsepace> with score
-- starting at 1 and with each read/write the score is incremented. When the
-- set is over capacity, the least frequently used entries (lowest scores in
-- the zset) are removed and corresponding keys deleted from the database.

local command = ARGV[1]
local lfu_key = "_LFU_::" .. ARGV[2]
local max_entries = ARGV[3]
local ct, rval, to_remove

-- GET or SET the key

if command == 'GET' then
    rval = redis.call('GET', KEYS[1])
else
    redis.call('SET', KEYS[1], ARGV[4])
    rval = true
end

if rval == nil then
    return
end

redis.call('ZINCRBY', lfu_key, 1, KEYS[1])
ct = redis.call('ZCOUNT', lfu_key, '-inf', '+inf')
if ct >= (max_entries + 10) then
    to_remove = redis.call('ZRANGE', lfu_key, 0, 9)
    redis.call('DEL', unpack(to_remove))
    redis.call('ZREMRANGEBYRANK', lfu_key, 0, 9)
end

return rval
