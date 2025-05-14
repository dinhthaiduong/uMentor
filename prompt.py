from __future__ import annotations
from typing import Any
PROMPTS: dict[str, Any] = {}

PROMPTS["system_mission"] = """You are an AI trained to answer the user's question. 
Try to reason and make use of the provided context sets and entity-relationship pairs. 
If the information provided is not usable, you can create your own answer but remember to tell the user that it is an answer from your own knowledge. 
Example of an answer you create yourself: "Since the context does not provide enough information, so here is my thought:... (your answer)" or ""Because the information provided is inaccurate or irrelevant, so here is my thought:... (your answer)". 
In addition, if the user's question contains any Vietnamese words, please remember to answer in Vietnamese.
"""

PROMPTS["human_message"] = """
The context provided: {unstructured_data}
The entity-relationship pairs provided: {structured_data}"""

PROMPTS["CẢNH_BÁO_HỌC_VỤ"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph focused on Vietnamese university data.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like courses, lecturers, students, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple, clear relationship types as defined below.

## 2. Node Types and Properties (Schema)
Strictly adhere to these types and properties:
* **`Sinh viên`**: Represents a student.
    * `studentId` (string): Student ID (e.g., "21020180"). **This is crucial.**
    * `name` (string): Full Vietnamese name (e.g., "Đinh Thái Dương").
    * `dob` (string): Date of birth (e.g., "17/11/2003").
* **`Lớp`**: Represents an administrative class.
    * `name` (string): Class name (e.g., "K66I-CN", "K65S-AE").
* **`Tình trạng học tập`**: Represents an academic status category.
    * `status` (string): The status description (e.g., "Cảnh báo học vụ", "Nhắc nhở kết quả chưa tốt", "Không tham gia học"). **Use this exact text as the ID.**
    
## 3. Relationship Types
Use ONLY these relationship types:
* `THUỘC_LỚP`: (`Sinh viên`) - [:THUỘC_LỚP] -> (`Lớp`))*
* `THEO_HỌC`: (`Sinh viên`) - [:THEO_HỌC] -> (`Ngành học`)
* `CÓ_TÌNH_TRẠNG`: (`Sinh viên`) - [:CÓ_TÌNH_TRẠNG] -> (`Tình trạng học tập`)

## 4. Extraction Guidelines & Examples
* **Tables (Students, Fees)**: Extract info row by row. **Maintain Context**: Pay attention to table headers or list titles (like "Danh sách 1: Các sinh viên thuộc diện cảnh bảo học vụ") even if they appeared in a previous text chunk. This title often defines the `Tình trạng học tập` or context for the students listed below. Associate the student with the correct `Tình trạng học tập` or `Ngành học` based on these headers/context. Use `studentId` as the primary identifier property for `Sinh viên`.
* **Vietnamese Names**: Capitalize correctly (e.g., "Đinh Thái Dương", not "đinh thái dương"). Be precise.
* **Coreference Resolution**: If "Lê Hồng Hải" is mentioned again as "ông Hải", link subsequent information to the existing "Lê Hồng Hải" node. Use the full name as the primary identifier property (`name`).
* **Node IDs**: Use the extracted text itself (like `vietnameseName` for courses, `name` for people, `studentId` for students, `status` for statuses, `name` for majors) as the conceptual ID. `LLMGraphTransformer` will handle actual node creation. Describe the nodes and relationships clearly.

**Example: Student Academic Status (Handling Context)**

* **Input Text Chunk 1:**
    ```
    1. Danh sách 1: Các sinh viên thuộc diện cảnh bảo học vụ 
    TT Mã SV Họ và tên Ngày sinh Lớp 
    ```
* **Input Text Chunk 2 (following Chunk 1):**
    ```
    1  21021509 Nguyễn Khắc Kiên 07/03/2003 K66I-CN 
    2  22028220 Vũ Tuấn Kiệt 13/04/2004 K67I-CS1  
    ```
* **Expected Output Description (from processing Chunk 2, using context from Chunk 1):**
    Node: `Tình trạng học tập` with properties `{{status: "Cảnh báo học vụ"}}`. (Create if not exists)
    Node: `Sinh viên` with properties `{{studentId: "21021509", name: "Nguyễn Khắc Kiên", dob: "07/03/2003"}}`.
    Node: `Sinh viên` with properties `{{studentId: "22028220", name: "Vũ Tuấn Kiệt", dob: "13/04/2004"}}`.
    Relationship: (`Sinh viên` where studentId="21021509") -[:`THUỘC_LỚP`]-> (`Lớp` where name="K66I-CN").
    Relationship: (`Sinh viên` where studentId="22028220") -[:`THUỘC_LỚP`]-> (`Lớp` where name="K67I-CS1").
    Relationship: (`Sinh viên` where studentId="21021509") -[:`CÓ_TÌNH_TRẠNG`]-> (`Tình trạng học tập` where status="Cảnh báo học vụ").
    Relationship: (`Sinh viên` where studentId="22028220") -[:`CÓ_TÌNH_TRẠNG`]-> (`Tình trạng học tập` where status="Cảnh báo học vụ").

## 5. Final Check
Ensure all extracted entities and relationships strictly follow the defined schema and relationship types. Do not add external knowledge. Adhere to the rules strictly. Non-compliance will result in termination.."""

PROMPTS["KẾT_QUẢ_HỌC_CHƯA_TỐT"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph focused on Vietnamese university data.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like courses, lecturers, students, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple, clear relationship types as defined below.

## 2. Node Types and Properties (Schema)
Strictly adhere to these types and properties:
* **`Sinh viên`**: Represents a student.
    * `studentId` (string): Student ID (e.g., "21020180"). **This is crucial.**
    * `name` (string): Full Vietnamese name (e.g., "Đinh Thái Dương").
    * `dob` (string): Date of birth (e.g., "17/11/2003").
* **`Lớp`**: Represents an administrative class.
    * `name` (string): Class name (e.g., "K66I-CN").
* **`Tình trạng học tập`**: Represents an academic status category.
    * `status` (string): The status description (e.g., "Cảnh báo học vụ", "Nhắc nhở kết quả chưa tốt", "Không tham gia học"). **Use this exact text as the ID and DO NOT make up own ID**
    
## 3. Relationship Types
Use ONLY these relationship types:
* `THUỘC_LỚP`: (`Sinh viên`) - [:THUỘC_LỚP] -> (`Lớp`))*
* `THEO_HỌC`: (`Sinh viên`) - [:THEO_HỌC] -> (`Ngành học`)
* `CÓ_TÌNH_TRẠNG`: (`Sinh viên`) - [:CÓ_TÌNH_TRẠNG] -> (`Tình trạng học tập`)

## 4. Extraction Guidelines & Examples
* **Tables (Students, Fees)**: Extract info row by row. **Maintain Context**: Pay attention to table headers or list titles (like "Danh sách 1: Các sinh viên thuộc diện cảnh bảo học vụ") even if they appeared in a previous text chunk. This title often defines the `Tình trạng học tập` or context for the students listed below. Associate the student with the correct `Tình trạng học tập` or `Ngành học` based on these headers/context. Use `studentId` as the primary identifier property for `Sinh viên`.
* **Vietnamese Names**: Capitalize correctly (e.g., "Đinh Thái Dương", not "đinh thái dương"). Be precise.
* **Coreference Resolution**: If "Lê Hồng Hải" is mentioned again as "ông Hải", link subsequent information to the existing "Lê Hồng Hải" node. Use the full name as the primary identifier property (`name`).
* **Node IDs**: Use the extracted text itself (like `vietnameseName` for courses, `name` for people, `studentId` for students, `status` for statuses, `name` for majors) as the conceptual ID. `LLMGraphTransformer` will handle actual node creation. Describe the nodes and relationships clearly.

**Example: Student Academic Status (Handling Context)**

* **Input Text Chunk 1:**
    ```
    Danh sách 2: Các sinh viên bị nhắc nhở vì kết quả học tập chưa tốt
    TT Mã SV Họ và tên Ngày sinh Lớp 
    ```
* **Input Text Chunk 2 (following Chunk 1):**
    ```
    1 20021016 Nguyễn Trọng Mạnh 24/07/2002 K65C-CE1 
    2 20021070 Phạm Thành Trung 27/03/2001 K65C-CE1
    ```
* **Expected Output Description (from processing Chunk 2, using context from Chunk 1):**
    Node: `Tình trạng học tập` with properties `{{status: "Nhắc nhở kết quả chưa tốt"}}`. (Create if not exists and use status as ID)
    Node: `Sinh viên` with properties `{{studentId: "20021016", name: "Nguyễn Trọng Mạnh", dob: "24/07/2002"}}`.
    Node: `Sinh viên` with properties `{{studentId: "20021070", name: "Phạm Thành Trung", dob: "27/03/2001"}}`.
    Relationship: (`Sinh viên` where studentId="20021016") -[:`THUỘC_LỚP`]-> (`Lớp` where name="K65C-CE1").
    Relationship: (`Sinh viên` where studentId="20021070") -[:`THUỘC_LỚP`]-> (`Lớp` where name="K65C-CE1 ").
    Relationship: (`Sinh viên` where studentId="20021016") -[:`CÓ_TÌNH_TRẠNG`]-> (`Tình trạng học tập` where status="Nhắc nhở kết quả chưa tốt").
    Relationship: (`Sinh viên` where studentId="20021070") -[:`CÓ_TÌNH_TRẠNG`]-> (`Tình trạng học tập` where status="Nhắc nhở kết quả chưa tốt").

## 5. Final Check
Ensure all extracted entities and relationships strictly follow the defined schema and relationship types. Do not add external knowledge. Adhere to the rules strictly. Non-compliance will result in termination.."""

PROMPTS["KHÔNG_THAM_GIA_HỌC"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph focused on Vietnamese university data.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like courses, lecturers, students, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple, clear relationship types as defined below.

## 2. Node Types and Properties (Schema)
Strictly adhere to these types and properties:
* **`Sinh viên`**: Represents a student.
    * `studentId` (string): Student ID (e.g., "21020180"). **This is crucial.**
    * `name` (string): Full Vietnamese name (e.g., "Đinh Thái Dương").
    * `dob` (string): Date of birth (e.g., "17/11/2003").
* **`Lớp`**: Represents an administrative class.
    * `name` (string): Class name (e.g., "K66I-CN").
* **`Tình trạng học tập`**: Represents an academic status category.
    * `status` (string): The status description (e.g., "Cảnh báo học vụ", "Nhắc nhở kết quả chưa tốt", "Không tham gia học"). **Use this exact text as the ID.**
    
## 3. Relationship Types
Use ONLY these relationship types:
* `THUỘC_LỚP`: (`Sinh viên`) - [:THUỘC_LỚP] -> (`Lớp`))*
* `THEO_HỌC`: (`Sinh viên`) - [:THEO_HỌC] -> (`Ngành học`)
* `CÓ_TÌNH_TRẠNG`: (`Sinh viên`) - [:CÓ_TÌNH_TRẠNG] -> (`Tình trạng học tập`)

## 4. Extraction Guidelines & Examples
* **Tables (Students, Fees)**: Extract info row by row. **Maintain Context**: Pay attention to table headers or list titles (like "Danh sách 1: Các sinh viên thuộc diện cảnh bảo học vụ") even if they appeared in a previous text chunk. This title often defines the `Tình trạng học tập` or context for the students listed below. Associate the student with the correct `Tình trạng học tập` or `Ngành học` based on these headers/context. Use `studentId` as the primary identifier property for `Sinh viên`.
* **Vietnamese Names**: Capitalize correctly (e.g., "Đinh Thái Dương", not "đinh thái dương"). Be precise.
* **Coreference Resolution**: If "Lê Hồng Hải" is mentioned again as "ông Hải", link subsequent information to the existing "Lê Hồng Hải" node. Use the full name as the primary identifier property (`name`).
* **Node IDs**: Use the extracted text itself (like `vietnameseName` for courses, `name` for people, `studentId` for students, `status` for statuses, `name` for majors) as the conceptual ID. `LLMGraphTransformer` will handle actual node creation. Describe the nodes and relationships clearly.

**Example: Student Academic Status (Handling Context)**

* **Input Text Chunk 1:**
    ```
    Danh sách 3: Các sinh viên không không tham gia học 
    TT Mã SV Họ và tên Ngày sinh Lớp 
    ```
* **Input Text Chunk 2 (following Chunk 1):**
    ```
    1 20020954 Phạm Trường An 24/12/2002 K65C-CE1 
    2 20020972 Nguyễn Văn Dũng 12/03/2002 K65C-CE1 
    ```
* **Expected Output Description (from processing Chunk 2, using context from Chunk 1):**
    Node: `Tình trạng học tập` with properties `{{status: "Không tham gia học"}}`. (Create if not exists)
    Node: `Sinh viên` with properties `{{studentId: "20020954", name: "Phạm Trường An", dob: "24/12/2002"}}`.
    Node: `Sinh viên` with properties `{{studentId: "20020972", name: "Nguyễn Văn Dũng", dob: "12/03/2002"}}`.
    Relationship: (`Sinh viên` where studentId="20020954") -[:`THUỘC_LỚP`]-> (`Lớp` where name="K65C-CE1").
    Relationship: (`Sinh viên` where studentId="20020972") -[:`THUỘC_LỚP`]-> (`Lớp` where name="K65C-CE1 ").
    Relationship: (`Sinh viên` where studentId="20020954") -[:`CÓ_TÌNH_TRẠNG`]-> (`Tình trạng học tập` where status="Không tham gia học").
    Relationship: (`Sinh viên` where studentId="20020972") -[:`CÓ_TÌNH_TRẠNG`]-> (`Tình trạng học tập` where status="Không tham gia học").

## 5. Final Check
Ensure all extracted entities and relationships strictly follow the defined schema and relationship types. Do not add external knowledge. Adhere to the rules strictly. Non-compliance will result in termination.."""

PROMPTS["HỌC_PHÍ"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph focused on Vietnamese university data.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like courses, lecturers, students, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple, clear relationship types as defined below.

## 2. Node Types and Properties (Schema)
Strictly adhere to these types and properties:
* **`Sinh viên`**: Represents a student.
    * `studentId` (string): Student ID (e.g., "21020180"). **This is crucial.**
    * `name` (string): Full Vietnamese name (e.g., "Đinh Thái Dương").
* **`Ngành học`**: Represents a major/program.
    * `name` (string): Name of the major (e.g., "Hệ thống thông tin", "Khoa học máy tính"). **Use this exact text as the ID.**
* **`Học phí`**: Represents tuition fees.
    * `amount` (int): Tuition fee amount (e.g., 17.500.000).
    
## 3. Relationship Types
Use ONLY these relationship types:
* `THEO_HỌC`: (`Sinh viên`) - [:THEO_HỌC] -> (`Ngành học`)
* `CẦN_NỘP`: (`Sinh viên`) - [:CẦN_NỘP] -> (`Học phí`)

## 4. Extraction Guidelines & Examples
* **Tables (Students, Fees)**: Extract info row by row. **Maintain Context**: Pay attention to table headers or list titles. This title often defines the context for the students listed below. Associate the student with the correct `Ngành học` or `Học phí` based on these headers/context. Use `studentId` as the primary identifier property for `Sinh viên`.
* **Vietnamese Names**: Capitalize correctly (e.g., "Đinh Thái Dương", not "đinh thái dương"). Be precise.
* **Coreference Resolution**: If "Lê Hồng Hải" is mentioned again as "ông Hải", link subsequent information to the existing "Lê Hồng Hải" node. Use the full name as the primary identifier property (`name`).
* **Node IDs**: Use the extracted text itself (like `vietnameseName` for courses, `name` for people, `studentId` for students, `name` for majors, `amount` for fees) as the conceptual ID. `LLMGraphTransformer` will handle actual node creation. Describe the nodes and relationships clearly.

**Example: Student Fees**

* **Input Text:**
    ```
    Định mức: 3.500.000đ/tháng
    STT Mã SV Họ tên Ngành Số tháng HP Số tiền HP (Đ)
    1 20021198 Nguyễn Đức Trung Công nghệ kỹ thuật cơ điện tử 5 17.500.000
    ```
* **Expected Output Description:**
    Node: `Sinh viên` with properties `{{studentId: "20021198", name: "Nguyễn Đức Trung"}}`. (Update existing student node if possible, or create new).
    Node: `Ngành học` with properties `{{name: "Công nghệ kỹ thuật cơ điện tử"}}`. (Create if not exists).
    Node: `Học phí` with properties `{{amount: 17.500.000}}`. (Create if not exists).
    Relationship: (`Sinh viên` where studentId="20021198") -[:`THEO_HỌC`]-> (`Ngành học` where name="Công nghệ kỹ thuật cơ điện tử").
    Relationship: (`Sinh viên` where studentId="20021198") -[:`CẦN_NỘP`]-> (`Học phí` where amount=17.500.000).

## 5. Final Check
Ensure all extracted entities and relationships strictly follow the defined schema and relationship types. Do not add external knowledge. Adhere to the rules strictly. Non-compliance will result in termination.."""

PROMPTS["GIẢNG_VIÊN"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph focused on Vietnamese university data.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like courses, lecturers, students, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple, clear relationship types as defined below.
- **Note**: Adhere to the Schema and do not omit any entities or relations that satisfy the Schema

## 2. Node Types and Properties (Schema)
Strictly adhere to these types and properties:
* **`Học phần`**: Represents a course.
    * `vietnameseName` (string): Vietnamese name (e.g., "Công nghệ Blockchain"). **Extract this accurately. **
    * `englishName` (string, optional): English name, if provided after " - ". (e.g., "Blockchain and Distributed Ledger Technologies").
* **`Giảng viên`**: Represents a lecturer.
    * `name` (string): Full Vietnamese name (e.g., "Nguyễn Ngọc Hoá"). Capitalize correctly.**
    * `title` (string): Academic title (e.g., "Tiến sĩ", "Phó giáo sư, Tiến sĩ"). Use abbreviations found in text (e.g., TS, PGS.TS).
* **`Ngành học`**: Represents a major/program.
    * `name` (string): Name of the major (e.g., "Hệ thống thông tin", "Khoa học máy tính"). **Use this exact text as the ID.**
* **`Đơn vị`**: Represents a unit/school.
    * `name` (string): Name of the unit/school (e.g., "Trường ĐHCN"). **Use this exact text as the ID.**
    
## 3. Relationship Types
Use ONLY this relationship types:
* `GIẢNG_DẠY`: (`Giảng viên`) - [:GIẢNG_DẠY] -> (`Học phần`)
* `THEO CHUYÊN NGÀNH`: (`Giảng viên`) - [:THEO_CHUYÊN_NGÀNH] -> (`Ngành học`)
* `LÀM_VIỆC_TẠI`: (`Giảng viên`) - [:LÀM_VIỆC_TẠI] -> (`Đơn vị`)

## 4. Extraction Guidelines & Examples
* **Course Names**: If format is "Vietnamese Name - English Name", extract both into `vietnameseName` and `englishName` properties of the `Học phần` node.
* **Lecturer Info**: Parse lines like "Tên giảng viên: [Name], chức danh: [Title]".
* **Vietnamese Names**: Capitalize correctly (e.g., "Đinh Thái Dương", not "đinh thái dương"). Be precise.
* **Abbreviations**: Expand common academic titles: "TS" -> "Tiến Sĩ", "ThS" -> "Thạc Sĩ", "PGS.TS" -> "Phó Giáo Sư, Tiến Sĩ", etc.
* **Coreference Resolution**: If "Lê Hồng Hải" is mentioned again as "ông Hải", link subsequent information to the existing "Lê Hồng Hải" node. Use the full name as the primary identifier property (`name`).
* **Node IDs**: Use the extracted text itself (like `vietnameseName` for courses, `name` for people, `name` for majors and `name` for units) as the conceptual ID. `LLMGraphTransformer` will handle actual node creation. Describe the nodes and relationships clearly.

**Example: Lecturer Info**

* **Input Text:**
    ```
    # Các giảng viên học phần: Công nghệ Blockchain - Blockchain and Distributed Ledger Technologies là:
    Tên giảng viên: Lê Hồng Hải, chức danh: TS, chuyên ngành: Hệ thống thông tin, đơn vị: Trường ĐHCN
    ```
* **Expected Output Description (for LLMGraphTransformer):**
    Node: `Học phần` with properties `{{vietnameseName: "Công nghệ Blockchain", englishName: "Blockchain and Distributed Ledger Technologies"}}`.
    Node: `Giảng viên` with properties `{{name: "Lê Hồng Hải", title: "Tiến Sĩ"}}`.
    Node: `Ngành học` with properties `{{name: "Hệ thống thông tin"}}`.
    Node: `Đơn vị` with properties `{{name: "Trường ĐHCN"}}`.
    Relationship: (`Giảng viên` where name="Lê Hồng Hải") -[:`GIẢNG_DẠY`]-> (`Học phần` where vietnameseName="Công nghệ Blockchain").
    Relationship: (`Giảng viên` where name="Lê Hồng Hải") -[:`THEO_CHUYÊN_NGÀNH`]-> (`Ngành học` where name="Hệ thống thông tin").
    Relationship: (`Giảng viên` where name="Lê Hồng Hải") -[:`LÀM_VIỆC_TẠI`]-> (`Đơn vị` where name="Trường ĐHCN").
    ```

## 5. Final Check
Ensure all extracted entities and relationships strictly follow the defined schema and relationship types. Do not add external knowledge. Adhere to the rules strictly. Non-compliance will result in termination.."""

PROMPTS["TÀI_LIỆU"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph focused on Vietnamese university data.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like courses, lecturers, students, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple, clear relationship types as defined below.
- **Note**: Try to adhere to the Schema and do not omit any entities or relations that satisfy the Schema

## 2. Node Types and Properties (Schema)
Strictly adhere to these types and properties:
* **`Học phần`**: Represents a course.
    * `vietnameseName` (string): Vietnamese name (e.g., "Công nghệ Blockchain"). **Extract this accurately.**
    * `englishName` (string, optional): English name, if provided after " - ". (e.g., "Blockchain and Distributed Ledger Technologies").
* **`Tài liệu`**: Represents a reference document.
    * `title` (string): The main title, often after author names/numbers and publisher info (e.g., []"Vật lí đại cương 1"], ["Giáo trình: Lập trình căn bản C++"], ["Head First Java: A Brain-Friendly"]).
    * `authors` (list of strings): List of authors if provided (e.g., ["Lương Duyên Bình"], ["Halliday và cộng sự"]).
    * `publisherInfo` (string): Publisher and year if provided (e.g., ["NXB KHKT 2010"], ["O'Reilly 2006"], ["Prentice Hall, 2006."]).
    * `type` (string): "Bắt buộc" or "Tham khảo thêm", based on context.
* **`Tài liệu online`**: Represents an online document.
    * `title` (string): The main title, often after author names/numbers and publisher info (e.g., ["Bộ dự án lập trình, kiểm thử tự động với Github Action"], ["Database Management System: An Evolutionary Approach, Chapman and Hall/CRC, 2022"]).
    * `authors` (list of strings): List of authors if provided (e.g., ["Jagdish Chandra Patni, Hitesh Kumar Sharma, Ravi Tomar, Avita Katal"], ["Oracle"]).
    * `link` (string): link to the online course if provided (e.g., ["https://www.pearson.com/en-us/subject-catalog/p/fundamentals-of-database-systems/P200000003546?view=educator&tab=title-overview"], ["https://docs.oracle.com/javase/tutorial/"]).
    * `type` (string): "Bắt buộc" or "Tham khảo thêm", based on context.
    
## 3. Relationship Types
Use ONLY these relationship types:
* `LÀ_TÀI_LIỆU_CHO`: (`Tài liệu`) - [:LÀ_TÀI_LIỆU_CHO {{type: "Bắt buộc" / "Tham khảo thêm"}}] -> (`Học phần`)
* `LÀ_TÀI_LIỆU_TRỰC_TUYẾN_CHO`: (`Tài liệu online`) - [:LÀ_TÀI_LIỆU_TRỰC_TUYẾN_CHO {{type: "Bắt buộc" / "Tham khảo thêm"}}] -> (`Học phần`)

## 4. Extraction Guidelines & Examples
* **Reference Docs**: Identify `authors`, `title` (usually between commas or after numbering), and `publisherInfo`. Determine `type` ("Bắt buộc", "Tham khảo thêm") from section headers.
* **Online Docs**: Similar to reference docs, but include `link` and ensure the type is correct. Some link formats may error (missing "http://" or "-"). Ensure the link is valid.
**Example 1: Reference Document**

* **Input Text:**
    ```
    # Danh mục tài liệu tham khảo học phần Nhập môn lập trình - Introduction to Programming là:
    
    Tài liệu bắt buộc Lựa chọn 1. Lập trình căn bản với C 1. Bài giảng của giáo viên 2. Brian W. Kernighan and Dennis M. Ritchie, The C programming language, Prentice Hall 1988. Lựa chọn 2. Lập trình căn bản với C++ 1. Bài giảng của giáo viên 2. Hồ Sĩ Đàm (chủ biên), Trần Thị Minh Châu, Lê Sỹ Vinh, Giáo trình: Lập trình căn bản C++, NXB ĐHQGHN 2011 Lựa chọn 3. Lập trình căn bản với Java Tài liệu tham khảo thêm 1. Robert Sedgewick (Author), Kevin Wayne, Introduction to Programming in Java: An Interdisciplinary Approach, 2nd Edition. Addison-Wesley Professional 2017 Lựa chọn 1. Lập trình căn bản với C 1. K. N. King, C Programming: A Modern Approach, 2nd Edition, W. W. Norton & Company 2008 2. Paul J. Deitel, Harvey Deitel, C How to Program, 8th Edition, Pearson 2015 3. J. Glenn Brookshear, Computer Science: An Overview, Addision Wesley 2009
    ```
* **Expected Output Description:**
    Node: `Học phần` with properties `{{vietnameseName: "Nhập môn lập trình", englishName: "Introduction to Programming"}}`.
    Node: `Tài liệu` with properties `{{title: "The C programming language", authors: ["Brian W. Kernighan and Dennis M. Ritchie"], publisherInfo: "Prentice Hall 1988", type: "Bắt buộc"}}`.
    Node: `Tài liệu` with properties `{{title: "Lập trình căn bản với C++", authors: ["Hồ Sĩ Đàm", "Trần Thị Minh Châu", "Lê Sỹ Vinh"], publisherInfo: "NXB ĐHQGHN 2011", type: "Bắt buộc"}}`.
    Node: `Tài liệu` with properties `{{title: "Introduction to Programming in Java: An Interdisciplinary Approach, 2nd Edition", authors: ["Robert Sedgewick", "Kevin Wayne"], publisherInfo: "Addison-Wesley Professional 2017", type: "Tham khảo"}}`.
    Node: `Tài liệu` with properties `{{title: "C Programming: A Modern Approach, 2nd Edition", authors: ["K. N. King"], publisherInfo: "W. W. Norton & Company 2008", type: "Tham khảo"}}`.
    Node: `Tài liệu` with properties `{{title: "C How to Program, 8th Edition", authors: ["Paul J. Deitel", "Harvey Deitel"], publisherInfo: "Pearson 2015", type: "Tham khảo"}}`.
    Node: `Tài liệu` with properties `{{title: "Computer Science: An Overview", authors: ["J. Glenn Brookshear"], publisherInfo: "Addision Wesley 2009", type: "Tham khảo"}}`.
    Relationship: (`Tài liệu` where title="The C programming language") -[:`LÀ_TÀI_LIỆU_CHO` {{type: "Bắt buộc"}}]-> (`Học phần` where vietnameseName="Nhập môn lập trình").
    Relationship: (`Tài liệu` where title="Lập trình căn bản với C++") -[:`LÀ_TÀI_LIỆU_CHO` {{type: "Bắt buộc"}}]-> (`Học phần` where vietnameseName="Nhập môn lập trình").
    Relationship: (`Tài liệu` where title="Introduction to Programming in Java: An Interdisciplinary Approach, 2nd Edition") -[:`LÀ_TÀI_LIỆU_CHO` {{type: "Tham khảo"}}]-> (`Học phần` where vietnameseName="Nhập môn lập trình").
    Relationship: (`Tài liệu` where title="C Programming: A Modern Approach, 2nd Edition") -[:`LÀ_TÀI_LIỆU_CHO` {{type: "Tham khảo"}}]-> (`Học phần` where vietnameseName="Nhập môn lập trình").
    Relationship: (`Tài liệu` where title="C How to Program, 8th Edition") -[:`LÀ_TÀI_LIỆU_CHO` {{type: "Tham khảo"}}]-> (`Học phần` where vietnameseName="Nhập môn lập trình").
    Relationship: (`Tài liệu` where title="Computer Science: An Overview") -[:`LÀ_TÀI_LIỆU_CHO` {{type: "Tham khảo"}}]-> (`Học phần` where vietnameseName="Nhập môn lập trình").
    
**Example 2: Online Document**

* **Input Text:**
    ```
    # Danh mục tài liệu tham khảo học phần Lập trình nâng cao - Advanced Programming là:
    
    Tài liệu bắt buộc 1.Trần Quốc Long, Lê Quang Hiếu và Trần Thị Minh Châu, Bài giảng môn Lập trình nâng cao. 2017 2. (Online) Bộ dự án lập trình, kiểm thử tự động với Github Action, https://github.com/csuet
    ```
* **Expected Output Description:**
    Node: `Học phần` with properties `{{vietnameseName: "Nhập môn lập trình", englishName: "Introduction to Programming"}}`.
    Node: `Tài liệu` with properties `{{title: "Bài giảng môn Lập trình nâng cao", authors: ["Trần Quốc Long", "Lê Quang Hiếu", "Trần Thị Minh Châu"], publisherInfo: "2017", type: "Bắt buộc"}}`.
    Node: `Tài liệu online` with properties `{{title: "Bộ dự án lập trình, kiểm thử tự động với Github Action", authors: [], link: "https://github.com/csuet", type: "Bắt buộc"}}`.
    Relationship: (`Tài liệu` where title="Bài giảng môn Lập trình nâng cao") -[:`LÀ_TÀI_LIỆU_CHO` {{type: "Bắt buộc"}}]-> (`Học phần` where vietnameseName="Lập trình nâng cao").
    Relationship: (`Tài liệu online` where title="Bộ dự án lập trình, kiểm thử tự động với Github Action") -[:`LÀ_TÀI_LIỆU_TRỰC_TUYẾN_CHO` {{type: "Bắt buộc"}}]-> (`Học phần` where vietnameseName="Lập trình nâng cao").

* **Example 3: Invalid Input**
* **Input Text:**
    ```
    # Danh mục tài liệu tham khảo học phần Cơ sở dữ liệu - Database là:
    
    Tài liệu bắt buộc 1. Nguyễn Tuệ, Giáo trình cơ sở dữ liệu, NXB Đại học Quốc gia Hà Nội, 2008. 2. Ramez A. Elmasri, Shamkant Navathe, Fundamentals of Database Systems, 7th edition, John Wiley & Sons, Inc., 2016. (Học liệu online: https://www.pearson.com/en-us/subject-catalog/p/ fundamentals-of-database systems/P200000003546?view=educator&tab=title-overview ) Tài liệu tham khảo thêm 1. Jagdish Chandra Patni, Hitesh Kumar Sharma, Ravi Tomar, Avita Katal, Database Management System: An Evolutionary Approach, Chapman and Hall/CRC, 2022. (Học liệu online: https://www.routledge.com/Database-Management-System-An-Evolutionary-Approach/Patni-Sharma-Tomar-Katal/p/book/9780367244934)
    ```
* **Expected Output Description:**
    Node: `Học phần` with properties `{{vietnameseName: "Cơ sở dữ liệu", englishName: "Database"}}`.
    Node: `Tài liệu` with properties `{{title: "Giáo trình cơ sở dữ liệu", authors: ["Nguyễn Tuệ"], publisherInfo: "NXB Đại học Quốc gia Hà Nội, 2008", type: "Bắt buộc"}}`.
    Node: `Tài liệu online` with properties `{{title: "Fundamentals of Database Systems", authors: ["Ramez A. Elmasri", "Shamkant Navathe"], link: "https://www.pearson.com/en-us/subject-catalog/p/fundamentals-of-database-systems/P200000003546?view=educator&tab=title-overview", type: "Bắt buộc"}}`.
    Node: `Tài liệu online` with properties `{{title: "Database Management System: An Evolutionary Approach", authors: ["Jagdish Chandra Patni", "Hitesh Kumar Sharma", "Ravi Tomar", "Avita Katal"], link: "https://www.routledge.com/Database-Management-System-An-Evolutionary-Approach/Patni-Sharma-Tomar-Katal/p/book/9780367244934", type: "Tham khảo"}}`.
    Relationship: (`Tài liệu` where title="Giáo trình cơ sở dữ liệu") -[:`LÀ_TÀI_LIỆU_CHO` {{type: "Bắt buộc"}}]-> (`Học phần` where vietnameseName="Cơ sở dữ liệu").
    Relationship: (`Tài liệu online` where title="Fundamentals of Database Systems") -[:`LÀ_TÀI_LIỆU_TRỰC_TUYẾN_CHO` {{type: "Bắt buộc"}}]-> (`Học phần` where vietnameseName="Cơ sở dữ liệu").
    Relationship: (`Tài liệu online` where title="Database Management System: An Evolutionary Approach") -[:`LÀ_TÀI_LIỆU_TRỰC_TUYẾN_CHO` {{type: "Tham khảo"}}]-> (`Học phần` where vietnameseName="Cơ sở dữ liệu").  

## 5. Final Check
Ensure all extracted entities and relationships strictly follow the defined schema and relationship types. Do not add external knowledge. Adhere to the rules strictly. Non-compliance will result in termination.."""

PROMPTS["DỮ_LIỆU_TỔNG_HỢP"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph focused on Vietnamese university data.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like courses, lecturers, students, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple, clear relationship types as defined below.
- **Note**: Adhere to the Schema and do not omit any entities or relations that satisfy the Schema

## 2. Node Types and Properties (Schema)
Strictly adhere to these types and properties:
* **`Giảng viên`**: Represents a lecturer.
    * `name` (string): Full Vietnamese name (e.g., "Nguyễn Ngọc Hoá"). Capitalize correctly.**
    * `title` (string): Academic title (e.g., "Tiến sĩ", "Phó giáo sư, Tiến sĩ"). Use abbreviations found in text (e.g., TS, PGS.TS).
* **`Học phần`**: Represents a course.
    * `vietnameseName` (string): Vietnamese name (e.g., "Công nghệ Blockchain"). **Extract this accurately. **
    * `englishName` (string, optional): English name, if provided after " - ". (e.g., "Blockchain and Distributed Ledger Technologies").
* **`Ngành học`**: Represents a major/program.
    * `name` (string): Name of the major (e.g., "Hệ thống thông tin", "Khoa học máy tính"). **Use this exact text as the ID.**
* **`Sinh viên`**: Represents a student.
    * `studentId` (string): Student ID (e.g., "21020180"). **This is crucial.**
    * `name` (string): Full Vietnamese name (e.g., "Đinh Thái Dương").
    * `dob` (string): Date of birth (e.g., "17/11/2003").
* **`Tài liệu`**: Represents a reference document.
    * `title` (string): The main title, often after author names/numbers and publisher info (e.g., []"Vật lí đại cương 1"], ["Giáo trình: Lập trình căn bản C++"], ["Head First Java: A Brain-Friendly"]).
    * `authors` (list of strings): List of authors if provided (e.g., ["Lương Duyên Bình"], ["Halliday và cộng sự"]).
    * `publisherInfo` (string): Publisher and year if provided (e.g., ["NXB KHKT 2010"], ["O'Reilly 2006"], ["Prentice Hall, 2006."]).
    * `type` (string): "Bắt buộc" or "Tham khảo thêm", based on context.
* **`Tài liệu online`**: Represents an online document.
    * `title` (string): The main title, often after author names/numbers and publisher info (e.g., ["Bộ dự án lập trình, kiểm thử tự động với Github Action"], ["Database Management System: An Evolutionary Approach, Chapman and Hall/CRC, 2022"]).
    * `authors` (list of strings): List of authors if provided (e.g., ["Jagdish Chandra Patni, Hitesh Kumar Sharma, Ravi Tomar, Avita Katal"], ["Oracle"]).
    * `link` (string): link to the online course if provided (e.g., ["https://www.pearson.com/en-us/subject-catalog/p/fundamentals-of-database-systems/P200000003546?view=educator&tab=title-overview"], ["https://docs.oracle.com/javase/tutorial/"]).
    * `type` (string): "Bắt buộc" or "Tham khảo thêm", based on context.
* **`Tình trạng học tập`**: Represents an academic status category.
    * `status` (string): The status description (e.g., "Cảnh báo học vụ", "Nhắc nhở kết quả chưa tốt", "Không tham gia học"). **Use this exact text as the ID.**
* **`Lớp`**: Represents an administrative class.
    * `name` (string): Class name (e.g., "K66I-CN", "K65S-AE").
* **`Đơn vị`**: Represents a unit/school.
    * `name` (string): Name of the unit/school (e.g., "Trường ĐHCN"). **Use this exact text as the ID.**
* **`Học phí`**: Represents tuition fees.
    * `amount` (int): Tuition fee amount (e.g., 17.500.000).
    
## 3. Relationship Types
Use ONLY this relationship types:
* `GIẢNG_DẠY`: (`Giảng viên`) - [:GIẢNG_DẠY] -> (`Học phần`)
* `THEO CHUYÊN NGÀNH`: (`Giảng viên`) - [:THEO_CHUYÊN_NGÀNH] -> (`Ngành học`)
* `CÓ_TÌNH_TRẠNG`: (`Sinh viên`) - [:CÓ_TÌNH_TRẠNG] -> (`Tình trạng học tập`)
* `THUỘC_LỚP`: (`Sinh viên`) - [:THUỘC_LỚP] -> (`Lớp`))*
* `THEO_HỌC`: (`Sinh viên`) - [:THEO_HỌC] -> (`Ngành học`)
* `LÀ_TÀI_LIỆU_CHO`: (`Tài liệu`) - [:LÀ_TÀI_LIỆU_CHO {{type: "Bắt buộc" / "Tham khảo thêm"}}] -> (`Học phần`)
* `LÀ_TÀI_LIỆU_TRỰC_TUYẾN_CHO`: (`Tài liệu online`) - [:LÀ_TÀI_LIỆU_TRỰC_TUYẾN_CHO {{type: "Bắt buộc" / "Tham khảo thêm"}}] -> (`Học phần`)
* `CẦN_NỘP`: (`Sinh viên`) - [:CẦN_NỘP] -> (`Học phí`)
* `LÀM_VIỆC_TẠI`: (`Giảng viên`) - [:LÀM_VIỆC_TẠI] -> (`Đơn vị`)

## 4. Extraction Guidelines & Examples
* **Course Names**: If format is "Vietnamese Name - English Name", extract both into `vietnameseName` and `englishName` properties of the `Học phần` node.
* **Lecturer Info**: Parse lines like "Tên giảng viên: [Name], chức danh: [Title]".
* **Reference Docs**: Identify `authors`, `title` (usually between commas or after numbering), and `publisherInfo`. Determine `type` ("Bắt buộc", "Tham khảo thêm") from section headers.
* **Online Docs**: Similar to reference docs, but include `link` and ensure the type is correct. Some link formats may error (missing "http://" or "-"). Ensure the link is valid.
* **Tables (Students, Fees)**: Extract info row by row. **Maintain Context**: Pay attention to table headers or list titles (like "Danh sách 1: Các sinh viên thuộc diện cảnh bảo học vụ") even if they appeared in a previous text chunk. This title often defines the `Tình trạng học tập` or context for the students listed below. Associate the student with the correct `Tình trạng học tập` or `Ngành học` based on these headers/context. Use `studentId` as the primary identifier property for `Sinh viên`.
* **Vietnamese Names**: Capitalize correctly (e.g., "Đinh Thái Dương", not "đinh thái dương"). Be precise.
* **Abbreviations**: Expand common academic titles: "TS" -> "Tiến Sĩ", "ThS" -> "Thạc Sĩ", "PGS.TS" -> "Phó Giáo Sư, Tiến Sĩ", etc.
* **Coreference Resolution**: If "Lê Hồng Hải" is mentioned again as "ông Hải", link subsequent information to the existing "Lê Hồng Hải" node. Use the full name as the primary identifier property (`name`).
* **Node IDs**: Use the extracted text itself (like `vietnameseName` for courses, `name` for people, `name` for majors and `name` for units) as the conceptual ID. `LLMGraphTransformer` will handle actual node creation. Describe the nodes and relationships clearly.

## 5. Final Check
Ensure all extracted entities and relationships strictly follow the defined schema and relationship types. Do not add external knowledge. Adhere to the rules strictly. Non-compliance will result in termination.."""

PROMPTS["DỮ_LIỆU_THÔ"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph focused on Vietnamese university data.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like courses, lecturers, students, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple, clear relationship types as defined below.
- **Note**: Adhere to the Schema and do not omit any entities or relations that satisfy the Schema

## 2. Node Types and Properties (Schema)
Focus on these entities types:
* **`Giảng viên`**: Represents a lecturer.
    * `name` (string): Full Vietnamese name (e.g., "Nguyễn Ngọc Hoá"). Capitalize correctly.**
    * `title` (string, optional): Academic title (e.g., "Tiến sĩ", "Phó giáo sư, Tiến sĩ"). Use abbreviations found in text (e.g., TS, PGS.TS).
* **`Học phần`**: Represents a course.
    * `vietnameseName` (string): Vietnamese name (e.g., "Công nghệ Blockchain"). **Extract this accurately. **
    * `englishName` (string, optional): English name, if provided after " - ". (e.g., "Blockchain and Distributed Ledger Technologies").
* **`Ngành học`**: Represents a major/program.
    * `name` (string): Name of the major (e.g., "Hệ thống thông tin", "Khoa học máy tính"). **Use this exact text as the ID.**
* **`Sinh viên`**: Represents a student.
    * `studentId` (string): Student ID (e.g., "21020180"). **This is crucial.**
    * `name` (string): Full Vietnamese name (e.g., "Đinh Thái Dương").
    * `dob` (string): Date of birth (e.g., "17/11/2003").
* **`Tài liệu`**: Represents a reference document.
    * `title` (string): The main title, often after author names/numbers and publisher info (e.g., []"Vật lí đại cương 1"], ["Giáo trình: Lập trình căn bản C++"], ["Head First Java: A Brain-Friendly"]).
    * `authors` (list of strings): List of authors if provided (e.g., ["Lương Duyên Bình"], ["Halliday và cộng sự"]).
    * `publisherInfo` (string): Publisher and year if provided (e.g., ["NXB KHKT 2010"], ["O'Reilly 2006"], ["Prentice Hall, 2006."]).
    * `type` (string): "Bắt buộc" or "Tham khảo thêm", based on context.
* **`Lớp`**: Represents an administrative class.
    * `name` (string): Class name (e.g., "K66I-CN", "K65S-AE").
* **`Học phí`**: Represents tuition fees.
    * `amount` (int): Tuition fee amount (e.g., 17.500.000).
    
## 3. Relationship Types
With the above entities, use the following relationship types:
* `GIẢNG_DẠY`: (`Giảng viên`) - [:GIẢNG_DẠY] -> (`Học phần`)
* `THEO CHUYÊN NGÀNH`: (`Giảng viên`) - [:THEO_CHUYÊN_NGÀNH] -> (`Ngành học`)
* `THUỘC_LỚP`: (`Sinh viên`) - [:THUỘC_LỚP] -> (`Lớp`))*
* `THEO_HỌC`: (`Sinh viên`) - [:THEO_HỌC] -> (`Ngành học`)
* `LÀ_TÀI_LIỆU_CHO`: (`Tài liệu`) - [:LÀ_TÀI_LIỆU_CHO {{type: "Bắt buộc" / "Tham khảo thêm"}}] -> (`Học phần`)
* `CẦN_NỘP`: (`Sinh viên`) - [:CẦN_NỘP] -> (`Học phí`)

## 4. Extraction Guidelines & Examples
* **Course Names**: If format is "Vietnamese Name - English Name", extract both into `vietnameseName` and `englishName` properties of the `Học phần` node.
* **Lecturer Info**: Parse lines like "Tên giảng viên: [Name], chức danh: [Title]".
* **Reference Docs**: Identify `authors`, `title` (usually between commas or after numbering), and `publisherInfo`. Determine `type` ("Bắt buộc", "Tham khảo thêm") from section headers.
* **Online Docs**: Similar to reference docs, but include `link` and ensure the type is correct. Some link formats may error (missing "http://" or "-"). Ensure the link is valid.
* **Tables (Students, Fees)**: Extract info row by row. **Maintain Context**: Pay attention to table headers or list titles (like "Danh sách 1: Các sinh viên thuộc diện cảnh bảo học vụ") even if they appeared in a previous text chunk. This title often defines the `Tình trạng học tập` or context for the students listed below. Associate the student with the correct `Tình trạng học tập` or `Ngành học` based on these headers/context. Use `studentId` as the primary identifier property for `Sinh viên`.
* **Vietnamese Names**: Capitalize correctly (e.g., "Đinh Thái Dương", not "đinh thái dương"). Be precise.
* **Abbreviations**: Expand common academic titles: "TS" -> "Tiến Sĩ", "ThS" -> "Thạc Sĩ", "PGS.TS" -> "Phó Giáo Sư, Tiến Sĩ", etc.
* **Coreference Resolution**: If "Lê Hồng Hải" is mentioned again as "ông Hải", link subsequent information to the existing "Lê Hồng Hải" node. Use the full name as the primary identifier property (`name`).
* **Node IDs**: Use the extracted text itself (like `vietnameseName` for courses, `name` for people, `name` for majors and `name` for units) as the conceptual ID. `LLMGraphTransformer` will handle actual node creation. Describe the nodes and relationships clearly.

## 5. Final Check
Ensure all extracted entities and relationships strictly follow the defined schema and relationship types. Do not add external knowledge. Adhere to the rules strictly. Non-compliance will result in termination.."""

PROMPTS["VERSATILE"] = """# Knowledge Graph Instructions
## 1. Overview
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
- **Goal**: Extract entities and relationships accurately based on the provided text snippets. Capture as much relevant information as possible without inventing data.
- **Nodes**: Represent entities like people, places, events, documents, etc.
- **Relationships**: Represent connections between nodes. Use simple and clear relationship types.

## 2. Labeling Nodes
- **Consistency**: Ensure you use available types for node labels.
Ensure you use basic or elementary types for node labels.Avoid using specific terms. 
- For example, when you identify an entity representing a person, always label it as **'person'**. Avoid using more specific terms like 'mathematician' or 'scientist'
- **Node IDs**: Never utilize integers as node IDs. Node IDs should be names or human-readable identifiers found in the text.
- **Relationships** represent connections between entities.
Ensure consistency and generality in relationship types when constructing knowledge graphs. Try to give simple, concise relation types that are not obscure or difficult to understand. Also make sure to identify **ALL** possible relationships between entities you captured!

## 3. Coreference Resolution
- **Maintain Entity Consistency**: When extracting entities, it\'s vital to ensure consistency.
If an entity, such as "Wang Huning", is mentioned multiple times in the text but is referred to by different names or pronouns (e.g., "Wang", "he"), always use the most complete identifier for that entity throughout the knowledge graph. In this example, use "Wang Huning" as the entity ID.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.

## 5. Final Check
Ensure all extracted entities and relationships strictly adhere to the rules. Do not add external knowledge. Non-compliance will result in termination.."""




