DELETE FROM youth_members
WHERE id_member = :id_member
RETURNING id_member;
