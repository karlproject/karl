
UPDATE corpus SET all_but_body_vec =
  to_tsvector('english', title);

UPDATE corpus SET all_vec =
  setweight(to_tsvector('english', title), 'A') ||
  setweight(to_tsvector('english', COALESCE(body, '')), 'D');

-- CREATE INDEX corpus_title ON corpus
--   USING GIN (to_tsvector('english', title));

CREATE INDEX corpus_all ON corpus
  USING GIN (all_vec);

CREATE INDEX corpus_all_but_body ON corpus
  USING GIN (all_but_body_vec);

explain analyze SELECT id, title,
    ts_rank_cd(all_but_body_vec, to_tsquery('ali:*'))
  FROM corpus
  WHERE all_vec @@ to_tsquery('ali:*')
  ORDER BY 3 DESC LIMIT 5;

explain analyze SELECT id, title,
    ts_rank_cd(all_vec, to_tsquery('ali:*'))
  FROM corpus
  WHERE all_vec @@ to_tsquery('ali:*')
  ORDER BY 3 DESC LIMIT 5;

SELECT id, title,
    ts_rank_cd(all_but_body_vec, to_tsquery('ali:*'))
  FROM corpus
  WHERE all_vec @@ to_tsquery('ali:*')
  ORDER BY 3 DESC LIMIT 5;

SELECT id, title,
    ts_rank_cd(all_vec, to_tsquery('ali:*'))
  FROM corpus
  WHERE all_vec @@ to_tsquery('ali:*')
  ORDER BY 3 DESC LIMIT 5;
