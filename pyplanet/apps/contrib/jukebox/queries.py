class Queries:
	FULL = """
SET @karma_expanded_voting = {};
SET @local_max_rank = {};
SET @player_id = {};

SELECT
	m.id,
	m.uid,
	m.name,
	IF(ISNULL(m.author_nickname), m.author_login, m.author_nickname) AS author,
	FORMAT(SUM(IF(@karma_expanded_voting = 1 AND k.expanded_score IS NOT NULL, k.expanded_score, k.score)), 1) AS karma,
	lr.score AS local_record,
	IF(lr.amount <= @local_max_rank, lr.amount, @local_max_rank) AS local_record_count,
	IF(pr.player_rank <= @local_max_rank, pr.score, NULL) AS player_local,
	IF(pr.player_rank <= @local_max_rank, pr.player_rank, NULL) AS player_local_rank
FROM map m

LEFT JOIN karma k
	ON k.map_id = m.id

LEFT OUTER JOIN LATERAL (
	SELECT
		map_id,
		MIN(score) AS score,
		COUNT(id) AS amount
	FROM localrecord
	GROUP BY map_id
) lr
ON lr.map_id = m.id

LEFT OUTER JOIN LATERAL (
	SELECT
		player_id,
		score,
		RANK() OVER (PARTITION BY map_id ORDER BY score ASC) AS player_rank
	FROM localrecord
	WHERE map_id = m.id
) pr
ON pr.player_id = @player_id

WHERE m.id IN ({})
GROUP BY m.id, m.uid, m.name, lr.score
"""

	WITHOUT_RECS = """
SET @karma_expanded_voting = {};

SELECT
	m.id,
	m.uid,
	m.name,
	IF(ISNULL(m.author_nickname), m.author_login, m.author_nickname) AS author,
	FORMAT(SUM(IF(@karma_expanded_voting = 1 AND k.expanded_score IS NOT NULL, k.expanded_score, k.score)), 1) AS karma
FROM map m

LEFT JOIN karma k
	ON k.map_id = m.id

WHERE m.id IN ({})
GROUP BY m.id, m.uid, m.name
"""

	WITHOUT_KARMA = """
SET @local_max_rank = {};
SET @player_id = {};

SELECT
	m.id,
	m.uid,
	m.name,
	IF(ISNULL(m.author_nickname), m.author_login, m.author_nickname) AS author,
	lr.score AS local_record,
	IF(lr.amount <= @local_max_rank, lr.amount, @local_max_rank) AS local_record_count,
	IF(pr.player_rank <= @local_max_rank, pr.score, NULL) AS player_local,
	IF(pr.player_rank <= @local_max_rank, pr.player_rank, NULL) AS player_local_rank
FROM map m

LEFT OUTER JOIN LATERAL (
	SELECT
		map_id,
		MIN(score) AS score,
		COUNT(id) AS amount
	FROM localrecord
	GROUP BY map_id
) lr
ON lr.map_id = m.id

LEFT OUTER JOIN LATERAL (
	SELECT
		player_id,
		score,
		RANK() OVER (PARTITION BY map_id ORDER BY score ASC) AS player_rank
	FROM localrecord
	WHERE map_id = m.id
) pr
ON pr.player_id = @player_id

WHERE m.id IN ({})
GROUP BY m.id, m.uid, m.name, lr.score
"""
