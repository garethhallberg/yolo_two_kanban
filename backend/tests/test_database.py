import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.database.models import Base, User, KanbanBoard, KanbanColumn, KanbanCard

# Setup test database
@pytest.fixture(scope="module")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSession
    
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(test_db):
    db = test_db()
    try:
        yield db
    finally:
        db.close()


def test_user_model(session):
    """Test User model creation and relationships"""
    user = User(username="testuser", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    # Test user retrieval
    retrieved_user = session.query(User).filter_by(username="testuser").first()
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.hashed_password == "hashedpass"
    assert retrieved_user.is_active == True
    assert retrieved_user.created_at is not None
    # updated_at is None on initial creation, only set on updates
    # assert retrieved_user.updated_at is not None

def test_kanban_board_model(session):
    """Test KanbanBoard model creation and relationships"""
    user = User(username="boarduser", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    board = KanbanBoard(user_id=user.id, title="Test Board")
    session.add(board)
    session.commit()
    
    # Test board retrieval
    retrieved_board = session.query(KanbanBoard).filter_by(title="Test Board").first()
    assert retrieved_board is not None
    assert retrieved_board.title == "Test Board"
    assert retrieved_board.user_id == user.id
    assert retrieved_board.user == user

def test_kanban_column_model(session):
    """Test KanbanColumn model creation and relationships"""
    user = User(username="columnuser", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    board = KanbanBoard(user_id=user.id, title="Column Test Board")
    session.add(board)
    session.commit()
    
    column = KanbanColumn(board_id=board.id, title="Test Column", position=1.0)
    session.add(column)
    session.commit()
    
    # Test column retrieval
    retrieved_column = session.query(KanbanColumn).filter_by(title="Test Column").first()
    assert retrieved_column is not None
    assert retrieved_column.title == "Test Column"
    assert retrieved_column.position == 1.0
    assert retrieved_column.board == board

def test_kanban_card_model(session):
    """Test KanbanCard model creation and relationships"""
    user = User(username="carduser", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    board = KanbanBoard(user_id=user.id, title="Card Test Board")
    session.add(board)
    session.commit()
    
    column = KanbanColumn(board_id=board.id, title="Card Column", position=1.0)
    session.add(column)
    session.commit()
    
    card = KanbanCard(
        column_id=column.id,
        title="Test Card",
        description="Test Description",
        position=1.0,
        priority="medium"
    )
    session.add(card)
    session.commit()
    
    # Test card retrieval
    retrieved_card = session.query(KanbanCard).filter_by(title="Test Card").first()
    assert retrieved_card is not None
    assert retrieved_card.title == "Test Card"
    assert retrieved_card.description == "Test Description"
    assert retrieved_card.position == 1.0
    assert retrieved_card.priority == "medium"
    assert retrieved_card.column == column

def test_cascade_delete_board(session):
    """Test cascade delete when board is deleted"""
    user = User(username="cascadeuser", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    board = KanbanBoard(user_id=user.id, title="Cascade Test Board")
    session.add(board)
    session.commit()
    
    column = KanbanColumn(board_id=board.id, title="Cascade Column", position=1.0)
    session.add(column)
    session.commit()
    
    card = KanbanCard(
        column_id=column.id,
        title="Cascade Card",
        position=1.0,
        priority="medium"
    )
    session.add(card)
    session.commit()
    
    # Verify relationships exist
    assert len(board.columns) == 1
    assert len(column.cards) == 1
    
    # Delete board and test cascade
    session.delete(board)
    session.commit()
    
    # Verify cascade worked
    assert session.query(KanbanColumn).filter_by(id=column.id).first() is None
    assert session.query(KanbanCard).filter_by(id=card.id).first() is None

def test_cascade_delete_column(session):
    """Test cascade delete when column is deleted"""
    user = User(username="columncascade", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    board = KanbanBoard(user_id=user.id, title="Column Cascade Board")
    session.add(board)
    session.commit()
    
    column = KanbanColumn(board_id=board.id, title="Delete Column", position=1.0)
    session.add(column)
    session.commit()
    
    card1 = KanbanCard(column_id=column.id, title="Card 1", position=1.0, priority="medium")
    card2 = KanbanCard(column_id=column.id, title="Card 2", position=2.0, priority="high")
    session.add_all([card1, card2])
    session.commit()
    
    # Verify cards exist
    assert len(column.cards) == 2
    
    # Delete column and test cascade
    session.delete(column)
    session.commit()
    
    # Verify cascade worked
    assert session.query(KanbanCard).filter_by(id=card1.id).first() is None
    assert session.query(KanbanCard).filter_by(id=card2.id).first() is None

def test_position_ordering(session):
    """Test that cards and columns are ordered by position"""
    user = User(username="orderuser", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    board = KanbanBoard(user_id=user.id, title="Order Test Board")
    session.add(board)
    session.commit()
    
    # Create columns with different positions
    col1 = KanbanColumn(board_id=board.id, title="First", position=1.0)
    col2 = KanbanColumn(board_id=board.id, title="Second", position=2.0)
    col3 = KanbanColumn(board_id=board.id, title="Third", position=3.0)
    session.add_all([col1, col2, col3])
    session.commit()
    
    # Create cards with different positions in first column
    card1 = KanbanCard(column_id=col1.id, title="Card 1", position=1.0, priority="medium")
    card2 = KanbanCard(column_id=col1.id, title="Card 2", position=2.0, priority="medium")
    card3 = KanbanCard(column_id=col1.id, title="Card 3", position=3.0, priority="medium")
    session.add_all([card1, card2, card3])
    session.commit()
    
    # Test column ordering
    columns = session.query(KanbanColumn).filter_by(board_id=board.id).order_by(KanbanColumn.position).all()
    assert len(columns) == 3
    assert columns[0].title == "First"
    assert columns[1].title == "Second"
    assert columns[2].title == "Third"
    
    # Test card ordering
    cards = session.query(KanbanCard).filter_by(column_id=col1.id).order_by(KanbanCard.position).all()
    assert len(cards) == 3
    assert cards[0].title == "Card 1"
    assert cards[1].title == "Card 2"
    assert cards[2].title == "Card 3"

def test_json_tags_field(session):
    """Test JSON tags field serialization"""
    user = User(username="taguser", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    board = KanbanBoard(user_id=user.id, title="Tag Test Board")
    session.add(board)
    session.commit()
    
    column = KanbanColumn(board_id=board.id, title="Tag Column", position=1.0)
    session.add(column)
    session.commit()
    
    tags = ["urgent", "backend", "bug"]
    card = KanbanCard(
        column_id=column.id,
        title="Tagged Card",
        position=1.0,
        priority="high",
        tags=tags
    )
    session.add(card)
    session.commit()
    
    # Retrieve and verify tags
    retrieved_card = session.query(KanbanCard).filter_by(title="Tagged Card").first()
    assert retrieved_card is not None
    assert retrieved_card.tags == tags

def test_unique_board_per_user(session):
    """Test that only one board per user is allowed"""
    user = User(username="uniqueuser", hashed_password="hashedpass")
    session.add(user)
    session.commit()
    
    # Create first board
    board1 = KanbanBoard(user_id=user.id, title="First Board")
    session.add(board1)
    session.commit()
    
    # Try to create second board for same user
    board2 = KanbanBoard(user_id=user.id, title="Second Board")
    session.add(board2)
    
    # This should raise an integrity error due to unique constraint
    with pytest.raises(Exception):  # SQLite raises IntegrityError
        session.commit()