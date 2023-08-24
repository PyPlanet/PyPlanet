class Queries:
	CALCULATE_WITH_PARTITION = """
-- Reset the current ranks to insert new ones later one.
TRUNCATE TABLE rankings_rank;
-- Limit on maximum ranked records.
SET @ranked_record_limit = {};
-- Minimum amount of ranked records required to acquire a rank.
SET @minimum_ranked_records = {};
-- Total amount of maps active on the server.
SET @active_map_count = {};
-- Set the rank/current rank variables to ensure correct first calculation
INSERT INTO rankings_rank (player_id, average, calculated_at)
SELECT
	player_id, average, calculated_at
FROM (
	SELECT
		player_id,
		-- Calculation: the sum of the record ranks is combined with the ranked record limit times the amount of unranked maps.
		-- Divide this summed ranking by the amount of active maps on the server, and an average calculated rank will be returned.
		ROUND((SUM(player_rank) + (@active_map_count - COUNT(player_rank)) * @ranked_record_limit) / @active_map_count * 10000, 0) AS average,
		NOW() AS calculated_at,
		COUNT(player_rank) AS ranked_records_count
	FROM
	(
		SELECT
			id,
			map_id,
			player_id,
			score,
			RANK() OVER (PARTITION BY map_id ORDER BY score ASC) AS player_rank
		FROM localrecord
		WHERE map_id IN ({})
	) AS ranked_records
	WHERE player_rank <= @ranked_record_limit
	GROUP BY player_id
) grouped_ranks
WHERE ranked_records_count >= @minimum_ranked_records
"""

	CALCULATE_WITHOUT_PARTITION = """
-- Reset the current ranks to insert new ones later one.
TRUNCATE TABLE rankings_rank;
-- Limit on maximum ranked records.
SET @ranked_record_limit = {};
-- Minimum amount of ranked records required to acquire a rank.
SET @minimum_ranked_records = {};
-- Total amount of maps active on the server.
SET @active_map_count = {};
-- Set the rank/current rank variables to ensure correct first calculation
SET @player_rank = 0;
SET @current_rank = 0;
INSERT INTO rankings_rank (player_id, average, calculated_at)
SELECT
	player_id, average, calculated_at
FROM (
	SELECT
		player_id,
		-- Calculation: the sum of the record ranks is combined with the ranked record limit times the amount of unranked maps.
		-- Divide this summed ranking by the amount of active maps on the server, and an average calculated rank will be returned.
		ROUND((SUM(player_rank) + (@active_map_count - COUNT(player_rank)) * @ranked_record_limit) / @active_map_count * 10000, 0) AS average,
		NOW() AS calculated_at,
		COUNT(player_rank) AS ranked_records_count
	FROM
	(
		SELECT
			id,
			map_id,
			player_id,
			score,
			@player_rank := IF(@current_rank = map_id, @player_rank + 1, 1) AS player_rank,
			@current_rank := map_id
		FROM localrecord
		WHERE map_id IN ({})
		ORDER BY map_id, score ASC
	) AS ranked_records
	WHERE player_rank <= @ranked_record_limit
	GROUP BY player_id
) grouped_ranks
WHERE ranked_records_count >= @minimum_ranked_records
"""
