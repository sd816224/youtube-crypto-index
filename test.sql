SELECT *
FROM your_table
WHERE timestamp >= NOW() - INTERVAL 30 MINUTE;
