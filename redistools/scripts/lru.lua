-- LRU replacement strategy
--
-- Keys used in GET/SET are added to a zset _LFU_::<namsepace> with score
-- starting at the given timestamp and with each read/write the score is
-- updated again with the current timestamp. When the set is over capacity, the
-- least recently used entries (lowest scores in the zset) are removed and
-- corresponding keys deleted from the database.

local command = ARGV[1]
local current_timestamp = ARGV[2]
local lru_key = "_LRU_::" .. ARGV[3]
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


-- Add to LRU cache and clear least recently used entries

redis.call('ZADD', lru_key, current_timestamp, KEYS[1])
ct = redis.call('ZCARD', lru_key)
if ct >= (max_entries + 10) then
    to_remove = redis.call('ZRANGE', lru_key, 0, 9)
    redis.call('DEL', unpack(to_remove))
    redis.call('ZREMRANGEBYRANK', lru_key, 0, 9)
end

return rval
