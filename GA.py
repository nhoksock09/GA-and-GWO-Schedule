import random
import tkinter as tk
from tkinter import messagebox

def create_individual(classes, teachers, rooms, timeslots, subjects):
    individual = []
    for cls, info in classes.items():
        for sub in info["subjects"]:
            valid_teachers = [t for t, d in teachers.items() if sub in d["subjects"]]
            if not valid_teachers:
                continue
            teacher = random.choice(valid_teachers)
            subj_type = subjects.get(sub, "Lecture")
            valid_rooms = [r for r, d in rooms.items() if d["type"] == subj_type] or list(rooms.keys())
            room = random.choice(valid_rooms)
            slot = random.choice(timeslots)
            individual.append((cls, sub, teacher, room, slot))
    return individual


def repair(individual, teachers, rooms, timeslots, subjects):
    """Sửa nếu trùng lịch hoặc phòng sai loại"""
    fixed = []
    used_teacher, used_class, used_room = {}, {}, {}
    for (cls, sub, teacher, room, slot) in individual:
        while (teacher, slot) in used_teacher or (cls, slot) in used_class or (room, slot) in used_room:
            slot = random.choice(timeslots)
            room = random.choice(list(rooms.keys()))
        used_teacher[(teacher, slot)] = 1
        used_class[(cls, slot)] = 1
        used_room[(room, slot)] = 1

        subj_type = subjects.get(sub, "Lecture")
        if subj_type != rooms[room]["type"]:
            valid_rooms = [r for r, d in rooms.items() if d["type"] == subj_type]
            if valid_rooms:
                room = random.choice(valid_rooms)
        fixed.append((cls, sub, teacher, room, slot))
    return fixed


def fitness(individual, teachers, rooms, classes, subjects):
    penalty = 0
    used_teacher, used_class, used_room = {}, {}, {}

    for (cls, sub, teacher, room, slot) in individual:
        if (teacher, slot) in used_teacher: penalty += 10
        else: used_teacher[(teacher, slot)] = 1
        if (cls, slot) in used_class: penalty += 10
        else: used_class[(cls, slot)] = 1
        if (room, slot) in used_room: penalty += 8
        else: used_room[(room, slot)] = 1
        if rooms[room]["capacity"] < classes[cls]["students"]: penalty += 6
        subj_type = subjects.get(sub, "Lecture")
        if subj_type != rooms[room]["type"]: penalty += 4
        if slot not in teachers[teacher]["available"]: penalty += 5

    return 1 / (1 + penalty)


def selection(pop, fits):
    total = sum(fits)
    if total == 0:
        return random.sample(pop, 2)
    probs = [f / total for f in fits]
    return random.choices(pop, weights=probs, k=2)


def crossover(p1, p2):
    if len(p1) < 2: return p1, p2
    point = random.randint(1, len(p1) - 1)
    return p1[:point] + p2[point:], p2[:point] + p1[point:]


def mutate(ind, rate, teachers, rooms, timeslots):
    for i in range(len(ind)):
        if random.random() < rate:
            cls, sub, teacher, room, slot = ind[i]
            choice = random.choice(["room", "slot", "teacher"])
            if choice == "room":
                room = random.choice(list(rooms.keys()))
            elif choice == "slot":
                slot = random.choice(timeslots)
            elif choice == "teacher":
                valid_teachers = [t for t, d in teachers.items() if sub in d["subjects"]]
                if valid_teachers:
                    teacher = random.choice(valid_teachers)
            ind[i] = (cls, sub, teacher, room, slot)
    return ind


def genetic_algorithm(teachers, classes, subjects, rooms, timeslots, log,
                    pop_size=60, generations=200, mutation_rate=0.2):
    population = [create_individual(classes, teachers, rooms, timeslots, subjects)
                for _ in range(pop_size)]
    best_fit, best_ind, stagnation = 0, None, 0
    prev_best = 0

    for gen in range(generations):
        fits = [fitness(ind, teachers, rooms, classes, subjects) for ind in population]
        elites = sorted(zip(fits, population), key=lambda x: x[0], reverse=True)[:1]
        new_pop = [e[1] for e in elites]

        while len(new_pop) < pop_size:
            p1, p2 = selection(population, fits)
            c1, c2 = crossover(p1, p2)
            c1, c2 = mutate(c1, mutation_rate, teachers, rooms, timeslots), mutate(c2, mutation_rate, teachers, rooms, timeslots)
            c1, c2 = repair(c1, teachers, rooms, timeslots, subjects), repair(c2, teachers, rooms, timeslots, subjects)
            new_pop += [c1, c2]
        population = new_pop[:pop_size]

        gen_best = max(fits)
        if gen_best > best_fit:
            best_fit = gen_best
            best_ind = population[fits.index(gen_best)]
            stagnation = 0
        else:
            stagnation += 1

        # 🔥 adaptive mutation & re-injection
        if stagnation >= 30:
            for _ in range(5):
                population.append(create_individual(classes, teachers, rooms, timeslots, subjects))
            stagnation = 0
            mutation_rate = min(0.5, mutation_rate + 0.05)

        if gen % 20 == 0:
            avg_fit = sum(fits) / len(fits)
            log.insert(tk.END, f"Thế hệ {gen}: best={best_fit:.4f}, avg={avg_fit:.4f}\n")
            log.see(tk.END)
            log.update()

        if best_fit == 1.0:
            log.insert(tk.END, f"\n🎉 Lịch hoàn hảo ở thế hệ {gen}!\n")
            break

    log.insert(tk.END, f"\n🎯 Fitness cuối cùng: {best_fit:.4f}\n")
    return best_ind, best_fit


