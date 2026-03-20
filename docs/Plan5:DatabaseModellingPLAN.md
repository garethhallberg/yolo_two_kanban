## Plan: Database Modeling for Kanban MVP

**TL;DR**: Design and implement a normalized SQLite schema with proper relationships for boards, columns, and cards. The schema must align with frontend TypeScript types and support atomic AI operations. We'll add Alembic for migrations and create comprehensive Pydantic schemas for validation.

**Current State**:

- Only `User` model exists
- No Alembic migrations (using simple `create_all()`)
- Database file exists at `backend/kanban.db`
- Frontend types already defined in `frontend/lib/types/kanban.ts`

**Approach**: Build normalized relational schema with foreign keys, cascades, and proper indexing. Add Alembic for future schema evolution. Create Pydantic schemas matching frontend types.

---

### Steps

**Phase 1: Schema Design & Documentation**

1. Document final schema design in `docs/database_schema.md` with ER diagram
2. Review frontend types and map to database fields (note: frontend uses strings for IDs, DB uses integers)
3. Define priority as ENUM/SQLAlchemy type or string with constraint
4. Decide on position tracking strategy (float for reordering, integer with gaps)
5. Get user sign-off on schema before implementation

**Phase 2: SQLAlchemy Models** 6. Create `KanbanBoard` model with:

- id (Integer PK)
- user_id (Integer FK to users.id, unique constraint for 1 board per user)
- title (String)
- created_at, updated_at timestamps

7. Create `KanbanColumn` model with:
   - id (Integer PK)
   - board_id (Integer FK to kanban_boards.id, cascade delete)
   - title (String)
   - position (Float for flexible ordering)
   - color (String, nullable)
   - wip_limit (Integer, nullable)
   - timestamps
8. Create `KanbanCard` model with:
   - id (Integer PK)
   - column_id (Integer FK to kanban_columns.id, cascade delete)
   - title (String)
   - description (Text, nullable)
   - position (Float)
   - priority (String with check constraint: 'low','medium','high','critical')
   - assignee (String, nullable)
   - due_date (DateTime, nullable)
   - tags (JSON/SQLite JSON field for array of strings)
   - timestamps
9. Add relationships: User.board, Board.columns, Column.cards
10. Add indexes on foreign keys and frequently queried fields (position, due_date)

**Phase 3: Pydantic Schemas** 11. Create schemas for each model: - BoardBase, BoardCreate, BoardUpdate, BoardResponse - ColumnBase, ColumnCreate, ColumnUpdate, ColumnResponse - CardBase, CardCreate, CardUpdate, CardResponse 12. Ensure schemas match frontend types (convert string IDs to integers for DB, but API can use strings) 13. Add validation: priority enum, date formats, position numbers 14. Include nested response schemas for board with columns and cards

**Phase 4: Alembic Migration Setup** 15. Install alembic (`uv add alembic`) 16. Initialize alembic: `alembic init migrations` 17. Configure `alembic.ini` and `migrations/env.py` to use existing database 18. Generate initial migration with all three new tables 19. Test migration: downgrade/upgrade on fresh DB 20. Update `init_db()` to use alembic instead of `create_all()` OR keep both for dev convenience

**Phase 5: Database Connection & Utilities** 21. Add JSON serialization support for SQLite (sqlite3.register_adapter/convert) if needed for tags 22. Create utility functions: - get_user_board(user_id) - returns board with all relationships - reorder_positions(column_id) - recalculate positions after moves - validate_board_ownership(user_id, board_id) 23. Add database connection pooling configuration if needed

**Phase 6: Testing** 24. Write unit tests for models (relationships, constraints) 25. Write integration tests for CRUD operations using test database 26. Test cascade deletes (deleting board removes columns and cards) 27. Test position ordering within columns 28. Test priority constraint validation 29. Test JSON tags field serialization/deserialization 30. Ensure 80% coverage on database layer

**Phase 7: Integration & Documentation** 31. Update API routers to use new models (Part 6 dependency) 32. Document schema in `docs/database_schema.md` with: - Table definitions - Relationships diagram - Indexes - Constraints 33. Add database seed script for development (sample board with columns/cards) 34. Verify database file creation and schema on first run

---

### Relevant Files to Modify

**New Files**:

- `backend/src/database/models.py` - Add KanbanBoard, KanbanColumn, KanbanCard
- `backend/src/database/schemas.py` - Add all kanban schemas
- `alembic.ini` - Alembic configuration
- `migrations/` directory - Alembic migration scripts
- `migrations/env.py` - Alembic environment
- `migrations/versions/` - Migration versions
- `docs/database_schema.md` - Schema documentation

**Modified Files**:

- `backend/src/config/database.py` - Update init_db() to use alembic or keep create_all()
- `backend/pyproject.toml` - Add alembic dependency
- `backend/src/models/__init__.py` - Export new models if needed

---

### Verification

1. **Schema correctness**:
   - Run `alembic upgrade head` and verify all tables created with correct columns and constraints
   - Check foreign key relationships with PRAGMA foreign_key_list in SQLite
   - Verify indexes exist on position, foreign keys

2. **Model functionality**:
   - Create user, board, columns, cards via Python shell
   - Test relationships: user.board, board.columns, column.cards
   - Test cascade delete: delete board → columns/cards removed
   - Test unique constraint: create second board for same user should fail

3. **Schema validation**:
   - Attempt to create card with invalid priority → validation error
   - Test JSON tags field stores and retrieves arrays correctly
   - Test position ordering: create multiple cards, verify order by position

4. **Alembic migrations**:
   - Fresh database: `alembic upgrade head` creates all tables
   - Downgrade/upgrade cycle works without errors
   - Migration script is reproducible and idempotent

5. **Test coverage**:
   - Run `pytest --cov=backend/src/database` → ≥80% coverage
   - All database tests pass

6. **Documentation**:
   - `docs/database_schema.md` complete with ER diagram (use Mermaid or ASCII)
   - All fields, types, constraints documented
   - Frontend developers can understand data shape from schemas

---

### Decisions & Assumptions

- **ID type**: Database uses auto-incrementing integers. API will convert to/from strings for frontend compatibility.
- **Position tracking**: Float values allow inserting between existing positions without renumbering all rows (e.g., 1.0, 2.0, 3.0 → insert at 2.5). Simpler than integer gap management.
- **Tags storage**: SQLite JSON1 extension (built-in) to store tags as JSON array. Enables querying by tag if needed later.
- **Priority constraint**: Enforced at Pydantic schema level (application) and optionally at DB with CHECK constraint.
- **Alembic vs create_all**: Use Alembic for production-like migrations. Keep `create_all()` as fallback for dev convenience? Decision: Use Alembic exclusively to ensure migration discipline.
- **One board per user**: Enforced with unique constraint on `user_id` in kanban_boards table.
- **Cascade deletes**: ON DELETE CASCADE for foreign keys so removing board/column cleans up children.
- **Timestamps**: Use database server defaults (func.now()) for created_at, onupdate for updated_at.

---

### Further Considerations

1. **Soft deletes?** For MVP, use hard deletes. Consider soft delete flag if we need recovery.
2. **Board title uniqueness?** Not needed since 1 board per user.
3. **Column title uniqueness within board?** Allow duplicate column titles? Probably yes, but could add constraint if needed.
4. **Card position scope**: Position is per-column (not global). Queries filter by column_id and order by position.
5. **WIP limit enforcement**: Not enforced at DB level, just advisory field for UI.
6. **Assignee storage**: Simple string (username or email). No FK to users table yet (future enhancement).
7. **Due date timezone**: Store as naive datetime or timezone-aware? Use naive UTC for simplicity.
8. **Audit trail**: Not needed for MVP, but could add created_by/updated_by later.

---

### Dependencies

- **Blocks**: Part 6 (Backend API Development) depends on this being complete
- **Parallel**: None - this is foundational
- **Prerequisites**: Part 2 (scaffolding) complete, database connection working

---

### Risk Mitigation

- **Schema changes after implementation**: Alembic makes this safe. Document migration process.
- **Performance**: Indexes on position and foreign keys prevent slow queries as data grows.
- **Data integrity**: Foreign key constraints and cascade rules prevent orphaned rows.
- **Frontend mismatch**: Keep schemas in sync with `frontend/lib/types/kanban.ts`. Consider generating types from schemas or vice versa in future.

---

### Success Criteria

- All tables created with correct columns, types, constraints, and relationships
- Alembic migrations work forward and backward
- Pydantic schemas validate all input and output correctly
- Database tests achieve ≥80% coverage
- Schema documentation approved by user
- No runtime errors when API starts and initializes database

---

### Estimated Effort

- Schema design & documentation: 2 hours
- Model implementation: 2 hours
- Schema implementation: 2 hours
- Alembic setup & migrations: 2 hours
- Testing: 3 hours
- **Total**: ~11 hours (1.5 days)

---

**Questions for alignment**:

1. Should we use Alembic exclusively, or keep `create_all()` as a dev convenience fallback?
2. Do you want CHECK constraints on priority at the database level, or just Pydantic validation?
3. Should we implement soft deletes for any entities, or hard deletes throughout?
4. Do you approve the float-based position tracking strategy?
5. Should tags be stored as JSON (SQLite JSON1) or a separate join table for future querying?
