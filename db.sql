
create database Leads;
use Leads;
SHOW TABLES;

select * from leads.leads_leadsforms;


INSERT INTO leads_leadsforms (contact_name, company_name, mobile_number, alternate_number, email_address, lead_source, lead_type, lead_priority, lead_stage, expected_closing_date) 
VALUES 
('John Doe', 'A', '1234567890', '0987654321', 'johndoe@gmailcom', 'Web', 'New', 'High', 'Contacted', '2024-12-31'),
('Jane Smith', 'B', '2345678901', '8765432109', 'jansmith@gmailcom', 'Referral', 'Follow-up', 'Medium', 'In Progress', '2024-11-30'),
('Tom Brown', 'c', '3456789012', '7654321098', 'tombrown@gmailcom', 'Social Media', 'Initial', 'Low', 'Not Contacted', '2024-10-15'),
('Alice Johnson', 'D', '4567890123', '6543210987', 'alicejohnson@gmailcom', 'Email', 'New', 'High', 'Contacted', '2024-09-25'),
('Bob White', 'E', '5678901234', '5432109876', 'bobwhite@gmailcom', 'Referral', 'Follow-up', 'Medium', 'In Progress', '2024-10-20'),
('Charlie Green', 'F', '6789012345', '4321098765', 'charliegreen@gmailcom', 'Web', 'Initial', 'Low', 'Not Contacted', '2024-11-01'),
('David Blue', 'G', '7890123456', '3210987654', 'davidblue@gmailcom', 'Social Media', 'New', 'High', 'Contacted', '2024-12-15'),
('Eva Black', 'E', '8901234567', '2109876543', 'evablack@gmailcom', 'Email', 'Follow-up', 'Medium', 'In Progress', '2024-09-10'),
('Frank Grey', 'I', '9012345678', '1098765432', 'frankgrey@gmailcom', 'Referral', 'Initial', 'Low', 'Not Contacted', '2024-10-05'),
('Grace Red', 'J', '0123456789', '0987654321', 'gracered@gmailcom', 'Web', 'New', 'High', 'Contacted', '2024-11-25');


SET SQL_SAFE_UPDATES = 0;

DELETE FROM leads_leadsforms;


drop database Leads;






INSERT INTO leads.leads_leadsforms (
    contact_name, 
    company_name, 
    mobile_number, 
    alternate_number, 
    email_address, 
    lead_source, 
    lead_type, 
    lead_priority, 
    lead_stage, 
    expected_closing_date,
    QUOTE_NO, 
    INVOICE_DATE, 
    PO_STATUS, 
    Direct_Conversion_Value, 
    Lead_Owner, 
    QUOTE_STATUS, 
    QUOTE_VALUE, 
    Customer_Feedback, 
    BRANCH_LOCATION, 
    JOB_STATUS, 
    PAYMENT_STATUS, 
    customer_Type, 
    Invoice_Value, 
    Follow_Up, 
    Follow_Up_Notes, 
    campaign_name, 
    campaign_content, 
    campaign_terms
) VALUES (
    'John Doe',                -- contact_name
    'Acme Corp',               -- company_name
    '1234567890',              -- mobile_number
    '0987654321',              -- alternate_number (can be NULL)
    'johndoe@example.com',     -- email_address
    'Website',                 -- lead_source
    'Hot',                     -- lead_type
    'High',                    -- lead_priority
    'Cold',         -- lead_stage
    '2024-12-31',              -- expected_closing_date
    'Q12345',                  -- QUOTE_NO (can be NULL)
    '2024-10-28',              -- INVOICE_DATE (can be NULL)
    'Pending',                 -- PO_STATUS (can be NULL)
    5000.00,                   -- Direct_Conversion_Value (can be NULL)
    'Jane Smith',              -- Lead_Owner (can be NULL)
    'Completed',             -- QUOTE_STATUS (can be NULL)
    5000.00,                   -- QUOTE_VALUE (can be NULL)
    'Positive',                -- Customer_Feedback (can be NULL)
    'New York',                -- BRANCH_LOCATION (can be NULL)
    'Ongoing',                 -- JOB_STATUS (can be NULL)
    'PAID',             -- PAYMENT_STATUS (can be NULL)
    'Hot',                     -- customer_Type (can be NULL)
    5000.00,                   -- Invoice_Value (can be NULL)
    '2024-11-15',              -- Follow_Up (can be NULL)
    'Contact again in two weeks', -- Follow_Up_Notes (can be NULL)
    'Winter Campaign',         -- campaign_name (can be NULL)
    'Special discounts for new customers', -- campaign_content (can be NULL)
    'Terms and conditions apply' -- campaign_terms (can be NULL)
);

