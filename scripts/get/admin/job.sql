SELECT p.filename, p.name as name, p.time, p.timeReal, p.length, p.weight, j.id as jobId, j.date, j.date_until, j.date_done, j.notes, u.name as user, s.name as status, j.amount
    FROM print p
    INNER JOIN job j ON p.id = j.printId
    INNER JOIN status s ON j.statusId = s.id
    INNER JOIN user u ON j.userId = u.id
        WHERE s.name = '%s'