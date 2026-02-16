UPDATE youth_members
SET
    member_name      = COALESCE(:member_name, member_name),
    phone_number     = COALESCE(:phone_number, phone_number),
    t_shirt          = COALESCE(:t_shirt, t_shirt),
    food_allergy     = COALESCE(:food_allergy, food_allergy),
    sower            = COALESCE(:sower, sower),
    ministry_position= COALESCE(:ministry_position, ministry_position),
    date_birth       = COALESCE(:date_birth, date_birth),
    email            = COALESCE(:email, email),
    update_date      = NOW()
WHERE id_member = :id_member
RETURNING
    id_member,
    member_name,
    phone_number,
    t_shirt,
    food_allergy,
    sower,
    ministry_position,
    date_birth,
    email,
    create_date,
    update_date;
