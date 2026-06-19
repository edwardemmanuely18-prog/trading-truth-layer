class ClaimTemplate(Base):
    __tablename__ = "claim_templates"

    id = Column(Integer, primary_key=True)

    workspace_id = Column(Integer, index=True)

    name = Column(String)

    description = Column(Text)

    template_type = Column(String)

    included_member_ids_json = Column(Text)

    included_symbols_json = Column(Text)

    methodology_notes = Column(Text)

    visibility = Column(String)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime)
    updated_at = Column(DateTime)