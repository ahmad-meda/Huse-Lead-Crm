import json
import requests

def display_lead_details(lead_data):
        if not lead_data:
            print("[DEBUG] No lead data to display")
            return
        
        # Extract data from the nested structure if it exists
        if 'data' in lead_data:
            lead_data = lead_data['data']
        
        print("=" * 60)
        print("LEAD DETAILS")
        print("=" * 60)
        
        # Basic Information
        print("\n📋 BASIC INFORMATION:")
        if lead_data.get('id'): print(f"   Lead ID: {lead_data['id']}")
        if lead_data.get('name'): print(f"   Name: {lead_data['name']}")
        if lead_data.get('cFullName'): print(f"   Full Name: {lead_data['cFullName']}")
        if lead_data.get('firstName'): print(f"   First Name: {lead_data['firstName']}")
        if lead_data.get('middleName'): print(f"   Middle Name: {lead_data['middleName']}")
        if lead_data.get('lastName'): print(f"   Last Name: {lead_data['lastName']}")
        if lead_data.get('cPreferredName'): print(f"   Preferred Name: {lead_data['cPreferredName']}")
        if lead_data.get('cPreferredName2'): print(f"   Preferred Name 2: {lead_data['cPreferredName2']}")
        if lead_data.get('salutationName'): print(f"   Salutation: {lead_data['salutationName']}")
        if lead_data.get('title'): print(f"   Title: {lead_data['title']}")
        if lead_data.get('status'): print(f"   Status: {lead_data['status']}")
        if lead_data.get('cLeadStatus'): print(f"   Lead Status: {lead_data['cLeadStatus']}")
        if lead_data.get('source'): print(f"   Source: {lead_data['source']}")
        if lead_data.get('deleted'): print(f"   Deleted: {lead_data['deleted']}")
        
        # Contact Information
        print("\n📞 CONTACT INFORMATION:")
        if lead_data.get('emailAddress'): print(f"   Email: {lead_data['emailAddress']}")
        if lead_data.get('cEmailAddress'): print(f"   Email Address (Custom): {lead_data['cEmailAddress']}")
        if lead_data.get('phoneNumber'): print(f"   Phone: {lead_data['phoneNumber']}")
        if lead_data.get('cPaMobileNumber'): print(f"   Mobile: {lead_data['cPaMobileNumber']}")
        if lead_data.get('cLandlineNumber'): print(f"   Landline: {lead_data['cLandlineNumber']}")
        if lead_data.get('doNotCall'): print(f"   Do Not Call: {lead_data['doNotCall']}")
        if lead_data.get('emailAddressIsOptedOut'): print(f"   Email Opted Out: {lead_data['emailAddressIsOptedOut']}")
        if lead_data.get('emailAddressIsInvalid'): print(f"   Email Invalid: {lead_data['emailAddressIsInvalid']}")
        if lead_data.get('phoneNumberIsOptedOut'): print(f"   Phone Opted Out: {lead_data['phoneNumberIsOptedOut']}")
        if lead_data.get('phoneNumberIsInvalid'): print(f"   Phone Invalid: {lead_data['phoneNumberIsInvalid']}")
        
        # Email Address Data
        email_data = lead_data.get('emailAddressData', [])
        if email_data:
            print(f"   Email Data: {email_data}")
        
        # Phone Number Data
        phone_data = lead_data.get('phoneNumberData', [])
        if phone_data:
            print(f"   Phone Data: {phone_data}")
        
        # Personal Information
        print("\n👤 PERSONAL INFORMATION:")
        if lead_data.get('cGender'): print(f"   Gender: {lead_data['cGender']}")
        if lead_data.get('cDateOfBirth'): print(f"   Date of Birth: {lead_data['cDateOfBirth']}")
        if lead_data.get('cNationality'): print(f"   Nationality: {lead_data['cNationality']}")
        if lead_data.get('cMaritalStatus'): print(f"   Marital Status: {lead_data['cMaritalStatus']}")
        if lead_data.get('cIdType'): print(f"   ID Type: {lead_data['cIdType']}")
        if lead_data.get('cIdNumber'): print(f"   ID Number: {lead_data['cIdNumber']}")
        
        # Professional Information
        print("\n💼 PROFESSIONAL INFORMATION:")
        if lead_data.get('cJobTitle'): print(f"   Job Title: {lead_data['cJobTitle']}")
        if lead_data.get('cJobTitle3'): print(f"   Job Title 3: {lead_data['cJobTitle3']}")
        if lead_data.get('cCompanyName'): print(f"   Company Name: {lead_data['cCompanyName']}")
        if lead_data.get('cCompany'): print(f"   Company: {lead_data['cCompany']}")
        if lead_data.get('cBusinessEmail'): print(f"   Business Email: {lead_data['cBusinessEmail']}")
        if lead_data.get('cBusinessPhone'): print(f"   Business Phone: {lead_data['cBusinessPhone']}")
        if lead_data.get('industry'): print(f"   Industry: {lead_data['industry']}")
        if lead_data.get('website'): print(f"   Website: {lead_data['website']}")
        if lead_data.get('cBusinessCompanyAddress'): print(f"   Business Company Address: {lead_data['cBusinessCompanyAddress']}")
        if lead_data.get('cBusinessZipcode'): print(f"   Business Zipcode: {lead_data['cBusinessZipcode']}")
        
        # Personal Assistant Information
        print("\n👨‍💼 PERSONAL ASSISTANT INFORMATION:")
        if lead_data.get('cPaTitle'): print(f"   PA Title: {lead_data['cPaTitle']}")
        if lead_data.get('cPaFullName'): print(f"   PA Full Name: {lead_data['cPaFullName']}")
        
        # Address Information
        print("\n🏠 ADDRESS INFORMATION:")
        if lead_data.get('addressStreet'): print(f"   Street Address: {lead_data['addressStreet']}")
        if lead_data.get('addressCity'): print(f"   City: {lead_data['addressCity']}")
        if lead_data.get('addressState'): print(f"   State: {lead_data['addressState']}")
        if lead_data.get('addressCountry'): print(f"   Country: {lead_data['addressCountry']}")
        if lead_data.get('addressPostalCode'): print(f"   Postal Code: {lead_data['addressPostalCode']}")
        if lead_data.get('cBuildingVilla'): print(f"   Building/Villa: {lead_data['cBuildingVilla']}")
        
        # Residential Address Information
        print("\n🏡 RESIDENTIAL ADDRESS INFORMATION:")
        if lead_data.get('cResidentialStreetAddress'): print(f"   Residential Street: {lead_data['cResidentialStreetAddress']}")
        if lead_data.get('cResidentialBuildingOrVilla'): print(f"   Residential Building/Villa: {lead_data['cResidentialBuildingOrVilla']}")
        if lead_data.get('cResidentialArea'): print(f"   Residential Area: {lead_data['cResidentialArea']}")
        if lead_data.get('cResidentialCity'): print(f"   Residential City: {lead_data['cResidentialCity']}")
        if lead_data.get('cResidentialCountry'): print(f"   Residential Country: {lead_data['cResidentialCountry']}")
        
        # Spouse Information
        print("\n👫 SPOUSE INFORMATION:")
        if lead_data.get('cSpouseCompanyAddress'): print(f"   Spouse Company Address: {lead_data['cSpouseCompanyAddress']}")
        if lead_data.get('cSpouseMobileNumber'): print(f"   Spouse Mobile: {lead_data['cSpouseMobileNumber']}")
        if lead_data.get('cSpouseNationality'): print(f"   Spouse Nationality: {lead_data['cSpouseNationality']}")
        if lead_data.get('cSpouseDateOfBirth'): print(f"   Spouse Date of Birth: {lead_data['cSpouseDateOfBirth']}")
        if lead_data.get('cSpouseemailAddress'): print(f"   Spouse Email: {lead_data['cSpouseemailAddress']}")
        
        # Membership Information
        print("\n🎫 MEMBERSHIP INFORMATION:")
        if lead_data.get('cMembershipCategory'): print(f"   Membership Category: {lead_data['cMembershipCategory']}")
        if lead_data.get('cPaymentsMembershipCategory'): print(f"   Payments Membership Category: {lead_data['cPaymentsMembershipCategory']}")
        if lead_data.get('cApplicationDate'): print(f"   Application Date: {lead_data['cApplicationDate']}")
        if lead_data.get('cMembershipAccountSettlementMethod'): print(f"   Settlement Method: {lead_data['cMembershipAccountSettlementMethod']}")
        if lead_data.get('cJoiningFee'): print(f"   Joining Fee: {lead_data['cJoiningFee']}")
        if lead_data.get('cAnnualSubscription'): print(f"   Annual Subscription: {lead_data['cAnnualSubscription']}")
        if lead_data.get('cApprovalStatus'): print(f"   Approval Status: {lead_data['cApprovalStatus']}")
        
        # Payment Methods and Settlement
        payment_methods = lead_data.get('cPaymentMethod', [])
        if payment_methods:
            print(f"   Payment Methods: {', '.join(payment_methods)}")
        
        settlement_methods = lead_data.get('cIWishToSettleMyMembershipAccountBy', [])
        if settlement_methods:
            print(f"   Settlement Preferences: {', '.join(settlement_methods)}")
        
        # Valuable Aspects
        valuable_aspects = lead_data.get('cWhichAspectsAreMostValuableToYou', [])
        if valuable_aspects:
            print(f"   Most Valuable Aspects: {', '.join(valuable_aspects)}")
        
        # Payment Information
        print("\n💳 PAYMENT INFORMATION:")
        if lead_data.get('cPaymentInvoiceNo'): print(f"   Payment Invoice No: {lead_data['cPaymentInvoiceNo']}")
        if lead_data.get('cPaymentDateissued'): print(f"   Payment Date Issued: {lead_data['cPaymentDateissued']}")
        if lead_data.get('cPaymentMembershipName'): print(f"   Payment Membership Name: {lead_data['cPaymentMembershipName']}")
        if lead_data.get('cPaymantDuedate'): print(f"   Payment Due Date: {lead_data['cPaymantDuedate']}")
        
        # Opportunity Information
        print("\n💰 OPPORTUNITY INFORMATION:")
        if lead_data.get('opportunityAmount'): print(f"   Opportunity Amount: {lead_data['opportunityAmount']}")
        if lead_data.get('opportunityAmountCurrency'): print(f"   Opportunity Currency: {lead_data['opportunityAmountCurrency']}")
        if lead_data.get('opportunityAmountConverted'): print(f"   Opportunity Amount Converted: {lead_data['opportunityAmountConverted']}")
        
        # Signature Information
        print("\n✍️ SIGNATURE INFORMATION:")
        if lead_data.get('cApplicantsName'): print(f"   Applicant's Name: {lead_data['cApplicantsName']}")
        if lead_data.get('cSignature'): print(f"   Signature: {lead_data['cSignature']}")
        if lead_data.get('cDateSigned'): print(f"   Date Signed: {lead_data['cDateSigned']}")
        
        # System Information
        print("\n⚙️ SYSTEM INFORMATION:")
        if lead_data.get('createdAt'): print(f"   Created: {lead_data['createdAt']}")
        if lead_data.get('modifiedAt'): print(f"   Modified: {lead_data['modifiedAt']}")
        if lead_data.get('streamUpdatedAt'): print(f"   Stream Updated: {lead_data['streamUpdatedAt']}")
        if lead_data.get('convertedAt'): print(f"   Converted: {lead_data['convertedAt']}")
        if lead_data.get('createdById'): print(f"   Created By ID: {lead_data['createdById']}")
        if lead_data.get('createdByName'): print(f"   Created By: {lead_data['createdByName']}")
        if lead_data.get('modifiedById'): print(f"   Modified By ID: {lead_data['modifiedById']}")
        if lead_data.get('modifiedByName'): print(f"   Modified By: {lead_data['modifiedByName']}")
        if lead_data.get('assignedUserId'): print(f"   Assigned User ID: {lead_data['assignedUserId']}")
        if lead_data.get('assignedUserName'): print(f"   Assigned To: {lead_data['assignedUserName']}")
        
        # Teams Information
        teams_ids = lead_data.get('teamsIds', [])
        if teams_ids:
            print(f"   Teams IDs: {', '.join(teams_ids)}")
        
        teams_names = lead_data.get('teamsNames', {})
        if teams_names:
            print(f"   Teams Names: {teams_names}")
        
        # Campaign Information
        print("\n📢 CAMPAIGN INFORMATION:")
        if lead_data.get('campaignId'): print(f"   Campaign ID: {lead_data['campaignId']}")
        if lead_data.get('campaignName'): print(f"   Campaign Name: {lead_data['campaignName']}")
        
        # Account Information
        print("\n🏢 ACCOUNT INFORMATION:")
        if lead_data.get('accountName'): print(f"   Account Name: {lead_data['accountName']}")
        if lead_data.get('createdAccountId'): print(f"   Created Account ID: {lead_data['createdAccountId']}")
        if lead_data.get('createdAccountName'): print(f"   Created Account Name: {lead_data['createdAccountName']}")
        
        # Contact Information
        print("\n👥 CONTACT INFORMATION:")
        if lead_data.get('createdContactId'): print(f"   Created Contact ID: {lead_data['createdContactId']}")
        if lead_data.get('createdContactName'): print(f"   Created Contact Name: {lead_data['createdContactName']}")
        
        # Opportunity Information
        print("\n🎯 OPPORTUNITY INFORMATION:")
        if lead_data.get('createdOpportunityId'): print(f"   Created Opportunity ID: {lead_data['createdOpportunityId']}")
        if lead_data.get('createdOpportunityName'): print(f"   Created Opportunity Name: {lead_data['createdOpportunityName']}")
        
        # Follow Information
        print("\n👁️ FOLLOW INFORMATION:")
        if lead_data.get('isFollowed'): print(f"   Is Followed: {lead_data['isFollowed']}")
        
        followers_ids = lead_data.get('followersIds', [])
        if followers_ids:
            print(f"   Followers IDs: {', '.join(followers_ids)}")
        
        followers_names = lead_data.get('followersNames', {})
        if followers_names:
            print(f"   Followers Names: {followers_names}")
        
        # Additional Information
        print("\n💭 ADDITIONAL INFORMATION:")
        if lead_data.get('cReferredBy'): print(f"   Referred By: {lead_data['cReferredBy']}")
        if lead_data.get('description'): print(f"   Description: {lead_data['description']}")
        if lead_data.get('cWhatDoYouSeekToGainFromJoiningRufescent'): 
            print(f"   What to Gain: {lead_data['cWhatDoYouSeekToGainFromJoiningRufescent']}")
        if lead_data.get('cIndustriesOrSectorsWouldYouLikeToConn'): 
            print(f"   Industries to Connect: {lead_data['cIndustriesOrSectorsWouldYouLikeToConn']}")
        
        print("\n" + "=" * 60)