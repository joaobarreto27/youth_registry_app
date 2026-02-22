SELECT id_member,
    member_name,
    phone_number,
    t_shirt,
    food_allergy,
    sower,
    ministry_position,
    date_birth,
    email,
    create_date,
    update_date
FROM youth_members
WHERE id_member = :id_member;
