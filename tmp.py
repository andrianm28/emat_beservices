
lists_dict = {}
@app.get("/daily_energies", response_model=List[Energies])
async def fetch_energies():
    query = energies.select().order_by(energies.c.created_at.desc())
    lists = await database.fetch_all(query)
    lists_json = jsonable_encoder(lists)
    lists_dict[energies] = lists_json
    energy_mapping = {}
    for energy_m in lists_dict[energies]:
        key = energy_m['created_at'].split(' ')[0]
        if key not in energy_mapping:
            energy_mapping[key] = energy_m

    daily_energy = []
    previous_energy = None
    for  _, energy in energy_mapping.items():
        if not previous_energy:
            previous_energy = energy['energy']
            continue
        current_energy = energy['energy'] - previous_energy
        previous_energy = energy['energy']
        daily_energy.append({'id': energy['id'], 'created_at': energy['created_at'], 'energy': abs(current_energy)})

    print(daily_energy)
    print(len(daily_energy))
    return daily_energy