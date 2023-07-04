INSERT INTO `playground-s-11-d3df42f0.beam_test.purchases` VALUES
(1, 1, 50),
(2, 1, 100),
(3, 2, 25)
;

INSERT INTO `playground-s-11-d3df42f0.beam_test.client` VALUES
(1, 'first user', 'USA'),
(2, 'second user', 'MX')
;

SELECT *
FROM
  `playground-s-11-d3df42f0.beam_test.client` AS C
INNER JOIN `playground-s-11-d3df42f0.beam_test.purchases` AS P
  ON C.id = P.client_id
;

-- RESULTS
/*
    id	name	country	id_1	client_id	value
    2	second user	MX	3	2	25
    1	first user	USA	1	1	50
    1	first user	USA	2	1	100
*/