def remove_used_fields_and_return_next(data_object,
                                       main_fields,
                                       secondary_fields,
                                       optional_job_fields,
                                       optional_education_fields):
    for field, value in vars(data_object).items():
        if value is not None and value != "":
            if field in main_fields:
                main_fields.remove(field)
            if field in secondary_fields:
                secondary_fields.remove(field)
            if field in optional_job_fields:
                optional_job_fields.remove(field)
            if field in optional_education_fields:
                optional_education_fields.remove(field)

    if main_fields:
        return "main_fields", main_fields
    elif secondary_fields:
        return "secondary_fields", secondary_fields
    elif optional_job_fields:
        return "optional_job_fields", optional_job_fields
    elif optional_education_fields:
        return "optional_education_fields", optional_education_fields
    else:
        return None, []

def remove_fields_by_name_and_return_next(
    used_fields,
    main_fields,
    secondary_fields,
    optional_job_fields,
    optional_education_fields
):
    for field in used_fields:
        if field in main_fields:
            main_fields.remove(field)
        if field in secondary_fields:
            secondary_fields.remove(field)
        if field in optional_job_fields:
            optional_job_fields.remove(field)
        if field in optional_education_fields:
            optional_education_fields.remove(field)

    if main_fields:
        return "main_fields", main_fields
    elif secondary_fields:
        return "secondary_fields", secondary_fields
    elif optional_job_fields:
        return "optional_job_fields", optional_job_fields
    elif optional_education_fields:
        return "optional_education_fields", optional_education_fields
    else:
        return None, []

