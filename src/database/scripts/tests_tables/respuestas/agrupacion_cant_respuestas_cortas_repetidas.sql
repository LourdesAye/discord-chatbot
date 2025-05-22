-- evaluando : las preguntas cortas que sean marcadas como tal
SELECT r.texto, r.es_corta, count(*)
FROM respuestas r
WHERE LENGTH(TRIM(texto)) <= 10  -- o ajustá el límite
group by r.texto, r.es_corta -- todo lo que se muestra va en group by
order by count(*) desc
