local a = tonumber(redis.call('GET', KEYS[1]))
return tonumber(ARGV[1]) + a
