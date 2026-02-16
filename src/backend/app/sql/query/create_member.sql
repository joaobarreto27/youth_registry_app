INSERT INTO youth_members (
    member_name,
    phone_number,
    t_shirt,
    food_allergy,
    sower,
    ministry_position,
    date_birth,
    email
    )
VALUES (:member_name,
    phone_number,
    t_shirt,
    food_allergy,
    sower,
    ministry_position,
    date_birth,
    email)
RETURNING id_member,member_name, phone_number, t_shirt, food_allergy, sower, ministry_position, date_birth, email, create_date, update_date;
