import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List

from langchain_text_splitters import CharacterTextSplitter

from lfx.custom.custom_component.component import Component
from lfx.io import DropdownInput, HandleInput, IntInput, MessageTextInput, Output
from lfx.schema.data import Data
from lfx.schema.dataframe import DataFrame
from lfx.schema.message import Message
from lfx.utils.util import unescape_string


class SplitTextComponent(Component):
    display_name: str = "Split Text (Oracle 23ai)"
    description: str = "Split text into chunks and prepare for Oracle 23ai PDFCOLLECTION table storage."
    documentation: str = "https://docs.langflow.org/split-text"
    icon = "scissors-line-dashed"
    name = "OracleSplitText"

    inputs = [
        HandleInput(
            name="data_inputs",
            display_name="Input",
            info="The data with texts to split in chunks.",
            input_types=["Data", "DataFrame", "Message"],
            required=True,
        ),
        IntInput(
            name="chunk_overlap",
            display_name="Chunk Overlap",
            info="Number of characters to overlap between chunks.",
            value=200,
        ),
        IntInput(
            name="chunk_size",
            display_name="Chunk Size",
            info=(
                "The maximum length of each chunk. Text is first split by separator, "
                "then chunks are merged up to this size. "
                "Individual splits larger than this won't be further divided."
            ),
            value=1000,
        ),
        MessageTextInput(
            name="separator",
            display_name="Separator",
            info=(
                "The character to split on. Use \\n for newline. "
                "Examples: \\n\\n for paragraphs, \\n for lines, . for sentences"
            ),
            value="\n",
        ),
        MessageTextInput(
            name="text_key",
            display_name="Text Key",
            info="The key to use for the text column.",
            value="text",
            advanced=True,
        ),
        DropdownInput(
            name="keep_separator",
            display_name="Keep Separator",
            info="Whether to keep the separator in the output chunks and where to place it.",
            options=["False", "True", "Start", "End"],
            value="False",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Chunks (Oracle Format)", name="dataframe", method="split_text"),
    ]

    def _generate_id(self) -> str:
        """Generate a unique ID for PDF collection record."""
        return str(uuid.uuid4())

    def _docs_to_oracle_data(self, docs) -> list[Data]:
        """Convert documents to Oracle PDFCOLLECTION table format.
        
        Maps to Oracle 23ai PDFCOLLECTION table schema:
        - ID: VARCHAR2(100) - UUID primary key
        - TEXT: CLOB - Document text chunk
        - METADATA: CLOB - JSON metadata
        - EMBEDDING: VECTOR(384) - Will be populated by embedding component
        - CREATED_AT: TIMESTAMP - Auto-populated by DB default
        """
        oracle_data = []
        for idx, doc in enumerate(docs):
            # Generate unique ID for each chunk
            chunk_id = self._generate_id()
            
            # Prepare metadata as JSON CLOB
            metadata = doc.metadata if hasattr(doc, 'metadata') else {}
            metadata['chunk_index'] = idx
            metadata['source_id'] = metadata.get('source_id', self._generate_id())
            metadata_json = json.dumps(metadata, ensure_ascii=False, default=str)
            
            # Create data record compatible with Oracle PDFCOLLECTION
            oracle_record = Data(
                text=doc.page_content,
                data={
                    'id': chunk_id,
                    'text': doc.page_content,
                    'metadata': metadata_json,
                    'embedding': None,  # To be populated by embedding component
                    'created_at': datetime.utcnow().isoformat(),
                    'source_metadata': metadata
                }
            )
            oracle_data.append(oracle_record)
        
        return oracle_data

    def _fix_separator(self, separator: str) -> str:
        """Fix common separator issues and convert to proper format."""
        if separator == "/n":
            return "\n"
        if separator == "/t":
            return "\t"
        return separator

    def split_text_base(self):
        separator = self._fix_separator(self.separator)
        separator = unescape_string(separator)

        if isinstance(self.data_inputs, DataFrame):
            if not len(self.data_inputs):
                msg = "DataFrame is empty"
                raise TypeError(msg)

            self.data_inputs.text_key = self.text_key
            try:
                documents = self.data_inputs.to_lc_documents()
            except Exception as e:
                msg = f"Error converting DataFrame to documents: {e}"
                raise TypeError(msg) from e
        elif isinstance(self.data_inputs, Message):
            self.data_inputs = [self.data_inputs.to_data()]
            return self.split_text_base()
        else:
            if not self.data_inputs:
                msg = "No data inputs provided"
                raise TypeError(msg)

            documents = []
            if isinstance(self.data_inputs, Data):
                self.data_inputs.text_key = self.text_key
                documents = [self.data_inputs.to_lc_document()]
            else:
                try:
                    documents = [input_.to_lc_document() for input_ in self.data_inputs if isinstance(input_, Data)]
                    if not documents:
                        msg = f"No valid Data inputs found in {type(self.data_inputs)}"
                        raise TypeError(msg)
                except AttributeError as e:
                    msg = f"Invalid input type in collection: {e}"
                    raise TypeError(msg) from e
        try:
            # Convert string 'False'/'True' to boolean
            keep_sep = self.keep_separator
            if isinstance(keep_sep, str):
                if keep_sep.lower() == "false":
                    keep_sep = False
                elif keep_sep.lower() == "true":
                    keep_sep = True
                # 'start' and 'end' are kept as strings

            splitter = CharacterTextSplitter(
                chunk_overlap=self.chunk_overlap,
                chunk_size=self.chunk_size,
                separator=separator,
                keep_separator=keep_sep,
            )
            return splitter.split_documents(documents)
        except Exception as e:
            msg = f"Error splitting text: {e}"
            raise TypeError(msg) from e

    def split_text(self) -> DataFrame:
        """Split text and prepare for Oracle PDFCOLLECTION table insertion.
        
        Returns DataFrame with columns:
        - id: Unique identifier (VARCHAR2(100))
        - text: Text chunk (CLOB)
        - metadata: JSON metadata (CLOB)
        - embedding: Vector placeholder (VECTOR(384))
        - created_at: Timestamp (TIMESTAMP)
        """
        split_docs = self.split_text_base()
        oracle_data = self._docs_to_oracle_data(split_docs)
        return DataFrame(oracle_data)
